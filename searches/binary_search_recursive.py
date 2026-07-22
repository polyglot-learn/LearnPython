"""Binary search, written recursively — the same algorithm, a different shape.

Recursion states the invariant directly: "the answer, if it exists, is in
values[lo..hi]". The cost is a stack frame per level, O(log n) deep, and
Python does not eliminate the tail call (default recursion limit: 1000).

Complexity: O(log n) time, O(log n) stack for this version.
"""

import sys


def binary_search_recursive(values: list[int], target: int) -> int:
    return _search(values, target, 0, len(values) - 1)


def _search(values: list[int], target: int, lo: int, hi: int) -> int:
    if lo > hi:  # empty range: not found
        return -1
    mid = lo + (hi - lo) // 2
    if values[mid] == target:
        return mid
    if values[mid] < target:
        return _search(values, target, mid + 1, hi)
    return _search(values, target, lo, mid - 1)


def search_answer(predicate, lo: int, hi: int) -> int:
    """Binary search over an *answer space*, not an array.

    Finds the smallest x in [lo, hi] with predicate(x) true, assuming the
    predicate is monotonic (false... false, true... true). This generalisation
    is what most competitive-programming binary searches actually are.
    """
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if predicate(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def main() -> None:
    data = [1, 3, 5, 7, 9, 11]
    print(f"recursive search(9) = {binary_search_recursive(data, 9)}")
    print(f"recursive search(2) = {binary_search_recursive(data, 2)}")
    print(f"stack depth for 10^6 elements ~= 20, limit is {sys.getrecursionlimit()}")

    # Integer square root as a monotone predicate search.
    n = 1_000_000
    root = search_answer(lambda x: x * x >= n, 0, n)
    print(f"isqrt({n}) = {root}")


if __name__ == "__main__":
    main()
