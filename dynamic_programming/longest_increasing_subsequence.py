"""Longest strictly increasing subsequence: the longest run of values that rise,
picked out of the sequence without reordering it.

The direct dynamic program keeps best[i], the length of the longest increasing
subsequence ending exactly at index i. Every such subsequence either starts at
i or arrives from some earlier j with values[j] < values[i], so best[i] is
1 + max(best[j]) over those j. That is O(n**2).

The faster method keeps tails[k], the smallest possible last value of any
increasing subsequence of length k+1. That list is sorted by construction, so
each new value can be placed with a binary search: it either extends the list
or replaces the first tail that is not smaller than it. Replacing never makes
an existing answer worse, only more extendable. This is the patience sorting
view, and it costs O(n log n).

Neither tails nor best holds the subsequence itself, so both versions store a
predecessor index per element and walk it back.

Complexity: O(n**2) and O(n log n) time, O(n) space for both.
"""

from bisect import bisect_left


def lis_quadratic(values: list[int]) -> list[int]:
    """O(n**2) dynamic program returning one longest increasing subsequence."""
    n = len(values)
    if n == 0:
        return []
    best = [1] * n
    prev = [-1] * n
    for i in range(n):
        for j in range(i):
            if values[j] < values[i] and best[j] + 1 > best[i]:
                best[i] = best[j] + 1
                prev[i] = j
    end = max(range(n), key=lambda i: best[i])
    return _walk_back(values, prev, end)


def lis_patience(values: list[int]) -> list[int]:
    """O(n log n) version using a binary search over the tails array."""
    n = len(values)
    if n == 0:
        return []
    tails: list[int] = []          # tails[k] = smallest tail of a length-k+1 LIS
    tail_index: list[int] = []     # index in values of each tail
    prev = [-1] * n
    for i, v in enumerate(values):
        k = bisect_left(tails, v)  # strictly increasing, so bisect_left
        if k > 0:
            prev[i] = tail_index[k - 1]
        if k == len(tails):
            tails.append(v)
            tail_index.append(i)
        else:
            tails[k] = v
            tail_index[k] = i
    return _walk_back(values, prev, tail_index[-1])


def _walk_back(values: list[int], prev: list[int], end: int) -> list[int]:
    out: list[int] = []
    while end != -1:
        out.append(values[end])
        end = prev[end]
    out.reverse()
    return out


def main() -> None:
    samples = [
        [10, 9, 2, 5, 3, 7, 101, 18],
        [3, 10, 2, 1, 20],
        [0, 1, 0, 3, 2, 3],
        [7, 7, 7, 7],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
    ]
    for values in samples:
        a = lis_quadratic(values)
        b = lis_patience(values)
        print(f"{values}")
        print(f"  quadratic: {a} (length {len(a)})")
        print(f"  patience:  {b} (length {len(b)})")
        assert len(a) == len(b)
        assert all(x < y for x, y in zip(b, b[1:]))  # genuinely increasing

    print("\nedge cases:")
    print("  empty:      ", lis_quadratic([]), lis_patience([]))
    print("  one element:", lis_quadratic([42]), lis_patience([42]))
    print("  duplicates only count once:", lis_patience([2, 2, 2]))


if __name__ == "__main__":
    main()
