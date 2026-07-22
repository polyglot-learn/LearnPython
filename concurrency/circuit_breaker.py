"""Circuit breaker: failing fast instead of piling onto a sick dependency.

When a downstream service is down, retrying every call makes things worse: the
caller's threads block on timeouts, queues back up, and the outage spreads. A
circuit breaker watches the failure count and, once it crosses a threshold,
trips open — every subsequent call is rejected immediately without touching the
dependency, which sheds load from both sides.

After a cooldown the breaker moves to half-open and admits a small number of
trial calls. Enough consecutive successes close it and normal service resumes;
a single failure trips it straight back open and restarts the cooldown. The
three states plus the trial window are the whole idea: fail fast while broken,
probe cheaply, and recover without a thundering herd of retries.
"""

import random
from collections.abc import Callable
from enum import Enum


class State(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"


class CircuitOpenError(RuntimeError):
    """Raised instead of calling the dependency while the circuit is open."""


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def advance(self, seconds: float) -> None:
        self.now += seconds


class CircuitBreaker:
    def __init__(self, clock: Clock, threshold: int = 3, cooldown: float = 5.0,
                 trial_successes: int = 2) -> None:
        self.clock = clock
        self.threshold = threshold
        self.cooldown = cooldown
        self.trial_successes = trial_successes
        self.state = State.CLOSED
        self.failures = 0
        self.successes = 0
        self.opened_at = 0.0

    def _trip(self) -> None:
        self.state = State.OPEN
        self.opened_at = self.clock.now
        self.failures = self.successes = 0

    def _maybe_probe(self) -> None:
        if (self.state is State.OPEN
                and self.clock.now - self.opened_at >= self.cooldown):
            self.state = State.HALF_OPEN
            self.successes = 0

    def call[T](self, fn: Callable[[], T]) -> T:
        self._maybe_probe()
        if self.state is State.OPEN:
            raise CircuitOpenError("circuit open — request shed")
        try:
            result = fn()
        except Exception:
            if self.state is State.HALF_OPEN:
                self._trip()  # one bad probe is enough; restart the cooldown
            else:
                self.failures += 1
                if self.failures >= self.threshold:
                    self._trip()
            raise
        if self.state is State.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.trial_successes:
                self.state = State.CLOSED
                self.failures = self.successes = 0
        else:
            self.failures = 0  # only consecutive failures count
        return result


def main() -> None:
    rng = random.Random(42)
    clock = Clock()
    breaker = CircuitBreaker(clock, threshold=3, cooldown=5.0, trial_successes=2)

    # The dependency is healthy, then breaks, then is repaired at t=20.
    def dependency() -> str:
        if 3.0 <= clock.now < 20.0:
            raise TimeoutError("upstream timeout")
        return f"payload-{rng.randrange(100)}"

    shed = 0
    print("t     state before -> after   outcome")
    for _ in range(30):
        before = breaker.state.value
        try:
            result = breaker.call(dependency)
            outcome = f"ok {result}"
        except CircuitOpenError:
            shed += 1
            outcome = "shed (no call made)"
        except TimeoutError as exc:
            outcome = f"FAILED {exc}"
        transition = f"{before} -> {breaker.state.value}"
        print(f"{clock.now:>5.1f} {transition:<24} {outcome}")
        clock.advance(1.0)

    print(f"\nfinal state: {breaker.state.value}; "
          f"{shed} calls shed without touching the dependency")

    print("\nedge cases")
    clock2 = Clock()
    b2 = CircuitBreaker(clock2, threshold=2, cooldown=1.0)
    print(f"  fresh breaker starts: {b2.state.value}")

    def flaky(fail: bool) -> Callable[[], str]:
        def inner() -> str:
            if fail:
                raise ValueError("boom")
            return "ok"
        return inner

    for pattern in (True, False, True):
        try:
            b2.call(flaky(pattern))
        except ValueError:
            pass
    print(f"  fail, success, fail -> still {b2.state.value} "
          f"(a success resets the consecutive count)")

    b2.state, b2.opened_at = State.OPEN, clock2.now
    try:
        b2.call(flaky(False))
    except CircuitOpenError as exc:
        print(f"  open circuit raises immediately: {exc}")
    clock2.advance(1.0)
    b2.call(flaky(False))
    print(f"  after cooldown, one good probe: {b2.state.value} "
          "(needs 2 in a row to close)")
    b2.call(flaky(False))
    print(f"  second good probe: {b2.state.value}")


if __name__ == "__main__":
    main()
