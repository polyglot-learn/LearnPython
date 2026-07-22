"""Quicksort: partition around a pivot, recurse on both sides.

Lomuto partitioning with the last element as pivot is the simplest to reason
about, and has a nasty worst case: on already-sorted input the pivot is always
the maximum, partitions are (n-1, 0), and the cost degrades to O(n^2) with
O(n) stack depth. Real implementations pick the pivot by median-of-three or at
random, and fall back to heapsort when recursion gets too deep (introsort).

Complexity: O(n log n) average, O(n^2) worst, O(log n) average stack.
Not stable.
"""

import random


def quick_sort(values: list[int]) -> list[int]:
    a = list(values)
    _quick_sort(a, 0, len(a) - 1)
    return a


def _quick_sort(a: list[int], lo: int, hi: int) -> None:
    while lo < hi:
        p = _partition(a, lo, hi)
        # Recurse into the smaller side, loop on the larger: caps stack at O(log n).
        if p - lo < hi - p:
            _quick_sort(a, lo, p - 1)
            lo = p + 1
        else:
            _quick_sort(a, p + 1, hi)
            hi = p - 1


def _partition(a: list[int], lo: int, hi: int) -> int:
    # Randomised pivot: makes the O(n^2) case improbable rather than adversarial.
    pick = random.randint(lo, hi)
    a[pick], a[hi] = a[hi], a[pick]
    pivot = a[hi]
    i = lo - 1
    for j in range(lo, hi):
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
    a[i + 1], a[hi] = a[hi], a[i + 1]
    return i + 1


def quick_sort_functional(values: list[int]) -> list[int]:
    """The one-liner everyone writes first: clear, but O(n) space per level."""
    if len(values) <= 1:
        return list(values)
    pivot = values[len(values) // 2]
    less = [x for x in values if x < pivot]
    equal = [x for x in values if x == pivot]
    greater = [x for x in values if x > pivot]
    return quick_sort_functional(less) + equal + quick_sort_functional(greater)


def main() -> None:
    print(quick_sort([10, 7, 8, 9, 1, 5]))
    print(quick_sort([2, 2, 2, 1]))
    print(quick_sort(list(range(10))))  # sorted input, no longer quadratic
    print(quick_sort_functional([10, 7, 8, 9, 1, 5]))


if __name__ == "__main__":
    main()
