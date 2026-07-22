"""Insertion sort: grow a sorted prefix one element at a time.

Take the next element and slide it left past everything larger. The way you
sort a hand of cards.

Complexity: O(n^2) worst/average, O(n) on nearly-sorted input, O(1) space,
stable. Its low constant factor is why real sorts (Timsort, introsort) fall
back to insertion sort for short runs — CPython does exactly this.
"""


def insertion_sort(values: list[int]) -> list[int]:
    a = list(values)
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        # Shift larger elements right to open a slot for `key`.
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def binary_insertion_sort(values: list[int]) -> list[int]:
    """Same shifts, but locate the slot with a binary search: O(n log n)
    comparisons, still O(n^2) moves."""
    from bisect import insort

    a: list[int] = []
    for value in values:
        insort(a, value)
    return a


def main() -> None:
    print(insertion_sort([5, 2, 4, 6, 1, 3]))
    print(insertion_sort([1, 2, 3]))
    print(binary_insertion_sort([5, 2, 4, 6, 1, 3]))
    print(insertion_sort([]))


if __name__ == "__main__":
    main()
