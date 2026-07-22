"""Retrying properly: exponential backoff, jitter, a budget, and a predicate.

Retrying immediately is the wrong reflex — it hits a struggling service hardest
exactly when it is least able to cope. Exponential backoff doubles the wait
after each attempt, so a caller that keeps failing gets out of the way quickly,
and a cap stops the delay growing without bound.

Jitter matters as much as the backoff. Without it, every client that failed at
the same moment retries at the same moment, and the load arrives as a spike;
randomising each delay spreads them out. Two more things make a retry loop safe
in production: an elapsed-time budget, so the total wait is bounded no matter
how many attempts fit inside it, and a predicate deciding what is worth
retrying at all — a timeout is transient, a 400 or a ValueError is not, and
retrying a non-idempotent write can double-charge someone.
"""

import itertools
import random
import time
from collections.abc import Callable
from dataclasses import dataclass


class TransientError(Exception):
    """Something worth trying again — a timeout, a 503, a dropped socket."""


class PermanentError(Exception):
    """A bad request or a logic error; retrying only wastes time."""


@dataclass
class RetryPolicy:
    attempts: int = 5
    base_delay: float = 0.05
    max_delay: float = 1.0
    budget: float = 10.0          # seconds of total elapsed time
    jitter: float = 0.5           # fraction of the delay that is randomised
    retry_on: type[Exception] | tuple[type[Exception], ...] = TransientError

    def delay_for(self, attempt: int, rng: random.Random) -> float:
        """Capped exponential backoff with proportional ("equal") jitter."""
        raw = min(self.max_delay, self.base_delay * 2 ** (attempt - 1))
        spread = raw * self.jitter
        return raw - spread + rng.uniform(0, 2 * spread)


def retry[T](fn: Callable[[], T], policy: RetryPolicy, rng: random.Random,
             sleep: Callable[[float], None] = time.sleep,
             now: Callable[[], float] = time.monotonic) -> T:
    """Call fn until it succeeds, the attempts run out, or the budget expires."""
    deadline = now() + policy.budget
    for attempt in itertools.count(1):
        try:
            return fn()
        except Exception as exc:
            if not isinstance(exc, policy.retry_on):
                print(f"    attempt {attempt}: {exc!r} is not retryable — "
                      "raising immediately")
                raise
            if attempt >= policy.attempts:
                print(f"    attempt {attempt}: failed, attempts exhausted")
                raise
            wait = policy.delay_for(attempt, rng)
            remaining = deadline - now()
            if wait >= remaining:
                # Sleeping would blow the budget, so give up now rather than
                # after a wait the caller has no time left for.
                print(f"    attempt {attempt}: failed, next wait {wait:.3f}s "
                      f"exceeds the {remaining:.3f}s left in the budget")
                raise
            print(f"    attempt {attempt}: {exc} — sleeping {wait:.3f}s")
            sleep(wait)
    raise AssertionError("unreachable")


def flaky(fail_times: int, error: Exception) -> Callable[[], str]:
    """Fails the first `fail_times` calls, then succeeds."""
    counter = itertools.count()

    def call() -> str:
        if next(counter) < fail_times:
            raise error
        return "200 OK"
    return call


def main() -> None:
    rng = random.Random(0)
    policy = RetryPolicy(attempts=5, base_delay=0.05, max_delay=0.4)

    print("succeeds on the 3rd attempt")
    print(f"  result: {retry(flaky(2, TransientError('503')), policy, rng)}")

    print("\nthe schedule without jitter doubles each time")
    plain = RetryPolicy(base_delay=0.05, max_delay=0.4, jitter=0.0)
    fixed = [f"{plain.delay_for(i, rng):.3f}" for i in range(1, 7)]
    print(f"  {fixed}  (capped at max_delay={plain.max_delay})")

    print("\nwith jitter, five clients failing together spread their retries")
    for client in range(5):
        client_rng = random.Random(client)
        row = [f"{policy.delay_for(i, client_rng):.3f}" for i in range(1, 5)]
        print(f"  client {client}: {row}")

    print("\na permanent error is not retried at all")
    try:
        retry(flaky(3, PermanentError("400 bad request")), policy, rng)
    except PermanentError as exc:
        print(f"  raised after 1 attempt: {exc}")

    print("\nattempts exhausted")
    try:
        retry(flaky(99, TransientError("timeout")), policy, rng)
    except TransientError as exc:
        print(f"  gave up: {exc}")

    print("\nbudget exhausted before the attempts are (simulated clock)")
    virtual = [0.0]
    tight = RetryPolicy(attempts=20, base_delay=1.0, max_delay=30.0, budget=5.0)
    try:
        retry(flaky(99, TransientError("timeout")), tight, random.Random(1),
              sleep=lambda s: virtual.__setitem__(0, virtual[0] + s),
              now=lambda: virtual[0])
    except TransientError:
        print(f"  gave up after {virtual[0]:.2f}s of simulated waiting, "
              f"well inside the {tight.budget}s budget")

    print("\nedge cases")
    print(f"  a function that never fails is called once: "
          f"{retry(lambda: 'immediate', policy, rng)}")
    once = RetryPolicy(attempts=1)
    try:
        retry(flaky(1, TransientError("nope")), once, rng)
    except TransientError:
        print("  attempts=1 means no retry at all")


if __name__ == "__main__":
    main()
