"""Sorting algorithms behind one signature: ``f(items, key) -> new list``.

Every function returns a new list, never mutates its input, and sorts by
``key(item)`` using ``<`` only, so any comparable keys work. Ties keep their
input order where noted ("stable").
"""

from collections.abc import Callable, Sequence
from heapq import heapify, heappop
from typing import Any

Key = Callable[[Any], Any]


def insertion_sort(items: Sequence, key: Key) -> list:
    """O(n^2), stable, fastest on tiny or nearly sorted input."""
    out = list(items)
    for i in range(1, len(out)):
        item, k = out[i], key(out[i])
        j = i - 1
        while j >= 0 and k < key(out[j]):
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = item
    return out


def merge_sort(items: Sequence, key: Key) -> list:
    """O(n log n), stable, O(n) extra space."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left, right = merge_sort(items[:mid], key), merge_sort(items[mid:], key)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        # `not (right < left)` keeps equal keys in input order (stable).
        if key(right[j]) < key(left[i]):
            out.append(right[j])
            j += 1
        else:
            out.append(left[i])
            i += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def quick_sort(items: Sequence, key: Key) -> list:
    """O(n log n) average, not stable. Three-way partition handles duplicates."""
    if len(items) <= 1:
        return list(items)
    pivot = key(items[len(items) // 2])
    less = [x for x in items if key(x) < pivot]
    equal = [x for x in items if not (key(x) < pivot) and not (pivot < key(x))]
    more = [x for x in items if pivot < key(x)]
    return quick_sort(less, key) + equal + quick_sort(more, key)


def heap_sort(items: Sequence, key: Key) -> list:
    """O(n log n), stable here because the index breaks ties."""
    heap = [(key(x), i, x) for i, x in enumerate(items)]
    heapify(heap)
    return [heappop(heap)[2] for _ in range(len(heap))]


def counting_sort(items: Sequence, key: Key) -> list:
    """O(n + range), stable. Keys must be ints."""
    if not items:
        return []
    keys = [key(x) for x in items]
    lo, hi = min(keys), max(keys)
    buckets: list[list] = [[] for _ in range(hi - lo + 1)]
    for item, k in zip(items, keys):
        buckets[k - lo].append(item)
    return [x for bucket in buckets for x in bucket]


def builtin_sort(items: Sequence, key: Key) -> list:
    """Timsort, the reference everything else is checked against."""
    return sorted(items, key=key)
