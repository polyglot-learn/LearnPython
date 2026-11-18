"""Search algorithms with one signature: ``f(items, target, key) -> index or -1``.

All except ``linear_search`` require ``items`` sorted ascending by ``key``.
"""

from collections.abc import Callable, Sequence
from math import isqrt
from typing import Any

Key = Callable[[Any], Any]


def linear_search(items: Sequence, target: Any, key: Key) -> int:
    """O(n). Works on unsorted data."""
    for i, item in enumerate(items):
        if key(item) == target:
            return i
    return -1


def binary_search(items: Sequence, target: Any, key: Key) -> int:
    """O(log n). Returns the leftmost match."""
    lo, hi = 0, len(items)
    while lo < hi:
        mid = (lo + hi) // 2
        if key(items[mid]) < target:
            lo = mid + 1
        else:
            hi = mid
    return lo if lo < len(items) and key(items[lo]) == target else -1


def jump_search(items: Sequence, target: Any, key: Key) -> int:
    """O(sqrt n): jump in blocks, then scan one block."""
    n = len(items)
    if n == 0:
        return -1
    step = max(1, isqrt(n))
    prev, cur = 0, step
    while prev < n and key(items[min(cur, n) - 1]) < target:
        prev, cur = cur, cur + step
    for i in range(prev, min(cur, n)):
        if key(items[i]) == target:
            return i
    return -1


def exponential_search(items: Sequence, target: Any, key: Key) -> int:
    """O(log i) where i is the answer's position: good when it is near the front."""
    n = len(items)
    if n == 0:
        return -1
    bound = 1
    while bound < n and key(items[bound]) < target:
        bound *= 2
    lo, hi = bound // 2, min(bound + 1, n)
    sub = binary_search(items[lo:hi], target, key)
    return -1 if sub == -1 else lo + sub


def interpolation_search(items: Sequence, target: Any, key: Key) -> int:
    """O(log log n) on uniformly spread numeric keys, O(n) worst case."""
    lo, hi = 0, len(items) - 1
    while lo <= hi and key(items[lo]) <= target <= key(items[hi]):
        a, b = key(items[lo]), key(items[hi])
        if a == b:
            return lo if a == target else -1
        pos = lo + int((target - a) * (hi - lo) / (b - a))
        k = key(items[pos])
        if k == target:
            while pos > lo and key(items[pos - 1]) == target:
                pos -= 1  # report the leftmost duplicate
            return pos
        if k < target:
            lo = pos + 1
        else:
            hi = pos - 1
    return -1
