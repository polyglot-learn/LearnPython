"""search_kit: find an item with a chosen search algorithm.

    >>> from searches.search_kit import find
    >>> find([1, 3, 5, 7], 5)
    2
    >>> find(["ann", "bob"], 3, algo="linear", key=len)
    0
"""

from collections.abc import Callable, Sequence
from typing import Any

from . import algorithms

ALGORITHMS: dict[str, Callable] = {
    "linear": algorithms.linear_search,
    "binary": algorithms.binary_search,
    "jump": algorithms.jump_search,
    "exponential": algorithms.exponential_search,
    "interpolation": algorithms.interpolation_search,
}

__all__ = ["ALGORITHMS", "find", "contains"]


def find(
    items: Sequence,
    target: Any,
    algo: str = "binary",
    key: Callable[[Any], Any] | None = None,
) -> int:
    """Index of the leftmost item whose key equals ``target``, or -1."""
    if algo not in ALGORITHMS:
        raise ValueError(f"unknown algorithm {algo!r}; choose from {sorted(ALGORITHMS)}")
    return ALGORITHMS[algo](items, target, key or (lambda x: x))


def contains(items: Sequence, target: Any, **kwargs: Any) -> bool:
    return find(items, target, **kwargs) != -1
