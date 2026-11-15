"""sort_kit: one ``sort()`` call over several sorting algorithms.

    >>> from sorts.sort_kit import sort
    >>> sort([3, 1, 2], algo="merge")
    [1, 2, 3]
    >>> sort(["bb", "a", "ccc"], key=len, reverse=True)
    ['ccc', 'bb', 'a']
"""

from collections.abc import Callable, Iterable
from typing import Any

from . import algorithms

ALGORITHMS: dict[str, Callable] = {
    "insertion": algorithms.insertion_sort,
    "merge": algorithms.merge_sort,
    "quick": algorithms.quick_sort,
    "heap": algorithms.heap_sort,
    "counting": algorithms.counting_sort,
    "builtin": algorithms.builtin_sort,
}

__all__ = ["ALGORITHMS", "sort", "is_sorted"]


def sort(
    items: Iterable,
    algo: str = "builtin",
    key: Callable[[Any], Any] | None = None,
    reverse: bool = False,
) -> list:
    """Return a new sorted list using the named algorithm."""
    try:
        func = ALGORITHMS[algo]
    except KeyError:
        raise ValueError(f"unknown algorithm {algo!r}; choose from {sorted(ALGORITHMS)}") from None
    data = list(items)
    key = key or (lambda x: x)
    if not reverse:
        return func(data, key)
    # Reverse in, stable sort, reverse out: descending order where equal
    # items still appear in their original order, like sorted(reverse=True).
    return func(data[::-1], key)[::-1]


def is_sorted(items: Iterable, key: Callable[[Any], Any] | None = None) -> bool:
    """True if items are in non-decreasing key order."""
    data = list(items)
    key = key or (lambda x: x)
    return all(not (key(b) < key(a)) for a, b in zip(data, data[1:]))
