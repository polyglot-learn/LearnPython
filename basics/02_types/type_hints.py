"""Type hints — documentation the tools can check.

Python stays dynamically typed at runtime: hints are *not* enforced, and a
hinted function will happily accept the wrong type. Their value is in review,
editor autocomplete, and static checkers like mypy or pyright, which read them
and fail the build before the code ever runs.

Modern syntax (3.10+) uses built-in generics and `|` for unions:
    list[int]        not  List[int]
    int | None       not  Optional[int]
"""

from collections.abc import Callable, Iterable


def total(values: Iterable[int]) -> int:
    return sum(values)


def first_word(text: str) -> str | None:
    """Return the first word, or None when the text is blank."""
    words = text.split()
    return words[0] if words else None


def apply_twice(fn: Callable[[int], int], value: int) -> int:
    return fn(fn(value))


Grid = list[list[int]]  # a type alias reads better than the raw type


def row_sums(grid: Grid) -> list[int]:
    return [sum(row) for row in grid]


def main() -> None:
    print(f"total([1, 2, 3]) = {total([1, 2, 3])}")
    print(f"first_word('hello there') = {first_word('hello there')!r}")
    print(f"first_word('   ') = {first_word('   ')!r}")
    print(f"apply_twice(lambda n: n * 3, 2) = {apply_twice(lambda n: n * 3, 2)}")
    print(f"row_sums([[1, 2], [3, 4]]) = {row_sums([[1, 2], [3, 4]])}")

    # Hints are not enforced at runtime — this runs, though mypy would object.
    print(f"total('abc') would fail at runtime, but hints alone do not stop it")

    # The annotations are readable data at runtime.
    print(f"first_word.__annotations__ = {first_word.__annotations__}")


if __name__ == "__main__":
    main()
