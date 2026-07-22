"""Token bucket and leaky bucket: two shapes of the same rate limit.

A token bucket holds up to `capacity` tokens and refills at `rate` tokens per
second. A request costs a token, so an idle client accumulates credit and may
spend it all at once: the long-run rate is capped at `rate` but a burst of up
to `capacity` is allowed through immediately. That is what you want in front
of an API, where clients are bursty and the backend has some headroom.

A leaky bucket instead drains at a fixed rate: arrivals queue up and depart
evenly, so the output is perfectly smooth and bursts are delayed rather than
passed on. Same average, different tail behaviour — burst tolerance versus
smoothing. Both are O(1) per request because the refill or drain is computed
lazily from the elapsed time instead of being ticked by a timer thread. This
file drives them from a fake clock, so it is deterministic and instant.
"""

from dataclasses import dataclass, field


class Clock:
    """A manually advanced clock, so tests need no real sleeping."""

    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def advance(self, seconds: float) -> float:
        self.now += seconds
        return self.now


@dataclass
class TokenBucket:
    rate: float           # tokens added per second
    capacity: float       # maximum burst
    clock: Clock
    tokens: float | None = None   # None means "start full"
    updated: float = field(default=0.0)

    def __post_init__(self) -> None:
        if self.tokens is None:
            self.tokens = self.capacity
        self.updated = self.clock.now

    def available(self) -> float:
        """Refill lazily from elapsed time — no timer thread needed."""
        elapsed = self.clock.now - self.updated
        self.updated = self.clock.now
        assert self.tokens is not None
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        return self.tokens

    def allow(self, cost: float = 1.0) -> bool:
        if self.available() >= cost:
            self.tokens -= cost
            return True
        return False

    def retry_after(self, cost: float = 1.0) -> float:
        """Seconds until `cost` tokens exist — what you put in Retry-After."""
        have = self.available()
        if have >= cost:
            return 0.0
        if self.rate == 0:
            return float("inf")
        return (cost - have) / self.rate


@dataclass
class LeakyBucket:
    """A queue draining at a fixed rate: accepted work departs on a schedule."""

    rate: float
    capacity: float          # how many items may be waiting
    clock: Clock
    next_departure: float = 0.0

    def __post_init__(self) -> None:
        self.next_departure = self.clock.now

    def submit(self) -> float | None:
        """Return the departure time, or None if the queue is full."""
        now = self.clock.now
        self.next_departure = max(now, self.next_departure)
        waiting = (self.next_departure - now) * self.rate
        if waiting >= self.capacity:
            return None
        depart = self.next_departure
        self.next_departure += 1.0 / self.rate
        return depart


def main() -> None:
    clock = Clock()
    tb = TokenBucket(rate=2.0, capacity=5.0, clock=clock)
    print("token bucket  rate=2/s cap=5   (+ allowed, . rejected)")
    marks = ["+" if tb.allow() else "." for _ in range(10)]
    print(f"  burst of 10 at t=0: {''.join(marks)}")
    steady = []
    for _ in range(10):
        clock.advance(0.5)
        steady.append("+" if tb.allow() else ".")
    print(f"  then 1 every 0.5s:  {''.join(steady)}")
    print("  the first 5 pass instantly on saved-up tokens — burst tolerance —")
    print("  and the rest are rejected outright, never delayed")

    clock = Clock()
    lb = LeakyBucket(rate=2.0, capacity=5.0, clock=clock)
    print("\nleaky bucket  rate=2/s queue=5")
    out = [lb.submit() for _ in range(10)]
    accepted = [f"{t:.1f}" for t in out if t is not None]
    print(f"  burst of 10 at t=0: departs at t={accepted}, "
          f"{sum(t is None for t in out)} dropped")
    print("  nothing leaves early: accepted work is smoothed to one every 0.5s,")
    print("  so downstream sees a flat rate at the cost of added latency")

    clock = Clock()
    tb = TokenBucket(rate=1.0, capacity=3.0, clock=clock)
    print("\nRetry-After from an empty bucket")
    for _ in range(3):
        tb.allow()
    print(f"  drained; retry_after(1)={tb.retry_after():.2f}s "
          f"retry_after(3)={tb.retry_after(3):.2f}s")
    clock.advance(1.5)
    print(f"  after 1.5s: tokens={tb.available():.1f} allow={tb.allow()}")

    print("\nedge cases")
    clock = Clock()
    tb = TokenBucket(rate=1.0, capacity=2.0, clock=clock)
    print(f"  cost larger than capacity never succeeds: {tb.allow(5)}")
    clock.advance(1_000)
    print(f"  a long idle period caps at capacity, not 1000: {tb.available()}")
    zero = TokenBucket(rate=0.0, capacity=1.0, clock=clock)
    print(f"  rate=0: one token then closed forever: "
          f"{zero.allow()} then {zero.allow()}")


if __name__ == "__main__":
    main()
