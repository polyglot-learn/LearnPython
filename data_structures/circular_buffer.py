"""Circular (ring) buffer: fixed memory, O(1) push and pop, oldest overwritten.

A pre-allocated array plus two indices that wrap with `% capacity`. Nothing is
ever allocated or shifted after construction, which is why ring buffers are the
default for audio pipelines, log tails, telemetry windows, and any producer /
consumer with bounded memory.

The full-vs-empty ambiguity (head == tail in both states) is resolved here by
tracking the count explicitly — the alternative is to waste one slot.
"""

from collections import deque


class RingBuffer[T]:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._data: list[T | None] = [None] * capacity
        self._head = 0  # next read position
        self._count = 0

    @property
    def is_full(self) -> bool:
        return self._count == self.capacity

    def push(self, item: T) -> T | None:
        """Append; when full, overwrite and return the evicted item."""
        evicted: T | None = None
        tail = (self._head + self._count) % self.capacity
        if self.is_full:
            evicted = self._data[self._head]
            self._head = (self._head + 1) % self.capacity
            self._count -= 1
            tail = (self._head + self._count) % self.capacity
        self._data[tail] = item
        self._count += 1
        return evicted

    def pop(self) -> T:
        if not self._count:
            raise IndexError("pop from empty buffer")
        item = self._data[self._head]
        self._data[self._head] = None
        self._head = (self._head + 1) % self.capacity
        self._count -= 1
        return item

    def __len__(self) -> int:
        return self._count

    def __iter__(self):
        for i in range(self._count):
            yield self._data[(self._head + i) % self.capacity]

    def __repr__(self) -> str:
        return f"RingBuffer({list(self)}, capacity={self.capacity})"


class MovingAverage:
    """A ring buffer's natural application: a fixed-window statistic."""

    def __init__(self, window: int) -> None:
        self.buffer = RingBuffer[float](window)
        self.total = 0.0

    def add(self, value: float) -> float:
        evicted = self.buffer.push(value)
        self.total += value - (evicted or 0.0)
        return self.total / len(self.buffer)


def main() -> None:
    ring = RingBuffer[int](4)
    for n in range(1, 5):
        ring.push(n)
    print(f"{ring}, full: {ring.is_full}")

    evicted = ring.push(5)
    print(f"pushed 5, evicted {evicted} -> {ring}")
    print(f"popped {ring.pop()} -> {ring}")

    avg = MovingAverage(3)
    for value in (10, 20, 30, 40, 50):
        print(f"  add {value}: 3-point average {avg.add(value):.2f}")

    # deque(maxlen=...) is the standard library's ring buffer.
    tail = deque(maxlen=3)
    for line in ("a", "b", "c", "d"):
        tail.append(line)
    print(f"deque(maxlen=3) keeps the last 3: {list(tail)}")


if __name__ == "__main__":
    main()
