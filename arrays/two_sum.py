"""Two sum: find two indices whose values add to a target.

The brute force is O(n^2). The trick is to invert the question: instead of
asking "does some later element pair with me?", ask "has the complement
already been seen?" — a dict lookup, O(1). One pass, O(n) time, O(n) space.

The two-pointer variant needs sorted input and O(1) space, but returns values
rather than original indices unless you carry them along.
"""


def two_sum(values: list[int], target: int) -> tuple[int, int] | None:
    seen: dict[int, int] = {}  # value -> index
    for i, value in enumerate(values):
        complement = target - value
        if complement in seen:
            return seen[complement], i
        seen[value] = i
    return None


def two_sum_sorted(values: list[int], target: int) -> tuple[int, int] | None:
    """Two pointers on sorted input: O(n) time, O(1) space."""
    lo, hi = 0, len(values) - 1
    while lo < hi:
        total = values[lo] + values[hi]
        if total == target:
            return lo, hi
        if total < target:
            lo += 1
        else:
            hi -= 1
    return None


def three_sum(values: list[int]) -> list[tuple[int, int, int]]:
    """All unique triples summing to zero: sort, then two-pointer per anchor."""
    a = sorted(values)
    out: list[tuple[int, int, int]] = []
    for i in range(len(a) - 2):
        if i and a[i] == a[i - 1]:
            continue  # skip duplicate anchors
        lo, hi = i + 1, len(a) - 1
        while lo < hi:
            total = a[i] + a[lo] + a[hi]
            if total == 0:
                out.append((a[i], a[lo], a[hi]))
                lo += 1
                while lo < hi and a[lo] == a[lo - 1]:
                    lo += 1
                hi -= 1
            elif total < 0:
                lo += 1
            else:
                hi -= 1
    return out


def main() -> None:
    print(two_sum([2, 7, 11, 15], 9))
    print(two_sum([3, 2, 4], 6))
    print(two_sum([1, 2], 100))
    print(two_sum_sorted([1, 3, 4, 6, 9], 10))
    print(three_sum([-1, 0, 1, 2, -1, -4]))


if __name__ == "__main__":
    main()
