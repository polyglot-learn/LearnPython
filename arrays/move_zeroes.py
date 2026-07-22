"""Move all zeroes to the end, keeping the order of the non-zero elements.

The read/write two-pointer pattern: `write` marks where the next kept element
belongs, `read` scans ahead. Everything between them is discardable. The same
skeleton solves remove-duplicates, remove-element, and compact-in-place.

O(n) time, O(1) space, at most n writes.
"""


def move_zeroes(values: list[int]) -> list[int]:
    a = list(values)
    write = 0
    for read in range(len(a)):
        if a[read] != 0:
            a[write], a[read] = a[read], a[write]
            write += 1
    return a


def remove_duplicates_sorted(values: list[int]) -> list[int]:
    """Same pattern: keep the first of each run, return the compacted prefix."""
    a = list(values)
    if not a:
        return a
    write = 1
    for read in range(1, len(a)):
        if a[read] != a[write - 1]:
            a[write] = a[read]
            write += 1
    return a[:write]


def remove_value(values: list[int], target: int) -> list[int]:
    a = list(values)
    write = 0
    for read in range(len(a)):
        if a[read] != target:
            a[write] = a[read]
            write += 1
    return a[:write]


def main() -> None:
    print(move_zeroes([0, 1, 0, 3, 12]))
    print(move_zeroes([0, 0, 0]))
    print(remove_duplicates_sorted([1, 1, 2, 2, 2, 3]))
    print(remove_value([3, 2, 2, 3], 3))


if __name__ == "__main__":
    main()
