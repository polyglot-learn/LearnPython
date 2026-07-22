"""`yield` — writing an iterator as an ordinary function.

Any function containing `yield` becomes a *generator function*. Calling it
runs no code; it returns a generator object. Each `next()` runs the body until
the next `yield`, hands back that value, and **freezes the function** — locals,
instruction pointer and all — until the following `next()`.

That laziness is the point: a generator can produce an infinite sequence, or
stream a huge file, using constant memory.
"""

import sys
from collections.abc import Iterator


def countdown(n: int) -> Iterator[int]:
    print("  (body starts running only on the first next())")
    while n > 0:
        yield n
        n -= 1


def naturals() -> Iterator[int]:
    """An infinite sequence — harmless, because nothing is precomputed."""
    n = 0
    while True:
        yield n
        n += 1


def read_records(lines: list[str]) -> Iterator[dict[str, str]]:
    """Stream-shaped parsing: one record in flight at a time."""
    for line in lines:
        name, _, role = line.partition(":")
        yield {"name": name.strip(), "role": role.strip()}


def flatten(items) -> Iterator[int]:
    """`yield from` delegates to a sub-iterator — recursion made readable."""
    for item in items:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item


def main() -> None:
    gen = countdown(3)
    print(f"calling countdown(3) returned {gen}")
    print(f"values: {list(gen)}")

    # Infinite generator, bounded at the consumer.
    from itertools import islice

    print(f"first 5 naturals: {list(islice(naturals(), 5))}")

    print(f"records: {list(read_records(['ada: engineer', 'grace: admiral']))}")
    print(f"flatten: {list(flatten([1, [2, [3, 4]], 5]))}")

    # Memory: a generator holds one value, a list holds them all.
    listed = [n * n for n in range(100_000)]
    lazy = (n * n for n in range(100_000))
    print(f"list  : {sys.getsizeof(listed):>8} bytes")
    print(f"genexp: {sys.getsizeof(lazy):>8} bytes")

    # A generator can also receive values and return one.
    def accumulator() -> Iterator[int]:
        total = 0
        while True:
            value = yield total
            if value is None:
                return
            total += value

    acc = accumulator()
    next(acc)  # prime it
    print(f"send 5 -> {acc.send(5)}, send 7 -> {acc.send(7)}")


if __name__ == "__main__":
    main()
