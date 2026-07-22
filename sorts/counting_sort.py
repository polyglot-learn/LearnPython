"""Counting sort: tally each value, then rebuild the array from the tallies.

Not a comparison sort, so the O(n log n) lower bound does not apply. It runs in
O(n + k) time and O(k) space for values in a range of size k — excellent when k
is small relative to n, disastrous when the values are sparse (sorting three
numbers around a million allocates a million counters).

The prefix-sum variant below is the stable one, and is the building block that
radix sort calls for each digit.
"""


def counting_sort(values: list[int]) -> list[int]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    counts = [0] * (hi - lo + 1)
    for v in values:
        counts[v - lo] += 1
    out: list[int] = []
    for offset, count in enumerate(counts):
        out.extend([offset + lo] * count)
    return out


def counting_sort_stable(values: list[int]) -> list[int]:
    """Prefix sums give each value its final slot, preserving input order."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    counts = [0] * (hi - lo + 1)
    for v in values:
        counts[v - lo] += 1
    # counts[i] becomes "how many elements are <= i", i.e. the end index.
    for i in range(1, len(counts)):
        counts[i] += counts[i - 1]
    out = [0] * len(values)
    for v in reversed(values):  # reversed keeps equal elements in order
        counts[v - lo] -= 1
        out[counts[v - lo]] = v
    return out


def main() -> None:
    print(counting_sort([4, 2, 2, 8, 3, 3, 1]))
    print(counting_sort([-3, -1, -2, 0]))  # negatives handled by the offset
    print(counting_sort_stable([4, 2, 2, 8, 3, 3, 1]))
    print(counting_sort([]))


if __name__ == "__main__":
    main()
