"""The iterator protocol — what `for` actually does.

An **iterable** can produce an iterator (`__iter__`). An **iterator** produces
the next value (`__next__`) and raises `StopIteration` when exhausted. Every
`for` loop is that protocol underneath:

    it = iter(obj)
    while True:
        try: item = next(it)
        except StopIteration: break
        ...

A list is iterable but not an iterator — you can loop it repeatedly. The
iterator you get from it is single-use. Knowing which one you hold explains
why a generator "goes empty" after one pass.
"""


class Countdown:
    """An iterable: each call to __iter__ hands back a fresh iterator."""

    def __init__(self, start: int) -> None:
        self.start = start

    def __iter__(self):
        return CountdownIterator(self.start)


class CountdownIterator:
    def __init__(self, current: int) -> None:
        self.current = current

    def __iter__(self):
        return self  # an iterator must also be iterable

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1


def main() -> None:
    # The manual version of a for loop.
    it = iter([10, 20])
    print(f"next -> {next(it)}")
    print(f"next -> {next(it)}")
    print(f"next with default -> {next(it, 'exhausted')}")

    xs = [1, 2, 3]
    print(f"list is iterable, not an iterator: {hasattr(xs, '__next__')}")
    print(f"iter(xs) is an iterator: {hasattr(iter(xs), '__next__')}")

    # A list can be looped twice; its iterator cannot.
    shared = iter(xs)
    print(f"first pass {list(shared)}, second pass {list(shared)}")
    print(f"the list itself: {list(xs)} then {list(xs)}")

    c = Countdown(3)
    print(f"custom iterable, pass 1: {list(c)}")
    print(f"custom iterable, pass 2: {list(c)}   (fresh iterator each time)")

    for n in Countdown(3):
        print(f"  tick {n}")


if __name__ == "__main__":
    main()
