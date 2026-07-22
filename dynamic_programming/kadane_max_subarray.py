"""Kadane's algorithm: the largest sum of any contiguous, non-empty slice.

The state is one number: the best sum of a slice that ends at the current
index. Extending the previous best slice or starting fresh at the current
element are the only two options, so curr = max(value, curr + value). If the
running sum ever goes negative it can only hurt whatever follows, which is why
starting fresh is ever worth doing. The overall answer is the largest value
that curr takes.

Tracking where each fresh start happened recovers the actual slice bounds.

The circular variant allows a slice that wraps past the end. Such a slice is
exactly the complement of a non-wrapping one, so the wrapping maximum equals
the total minus the minimum non-wrapping slice. The trap is an all-negative
array, where the minimum slice is the whole array and the complement is empty;
that case must fall back to the plain answer.

Complexity: O(n) time and O(1) space.
"""


def max_subarray_sum(values: list[int]) -> int:
    if not values:
        raise ValueError("max_subarray_sum needs at least one element")
    best = curr = values[0]
    for v in values[1:]:
        curr = max(v, curr + v)
        best = max(best, curr)
    return best


def max_subarray(values: list[int]) -> tuple[int, int, int]:
    """Return (sum, start, end) with end exclusive, for the best slice."""
    if not values:
        raise ValueError("max_subarray needs at least one element")
    best = curr = values[0]
    best_start = best_end = 0
    start = 0
    for i, v in enumerate(values[1:], start=1):
        if curr + v < v:  # dropping the prefix beats keeping it
            curr, start = v, i
        else:
            curr += v
        if curr > best:
            best, best_start, best_end = curr, start, i
    return best, best_start, best_end + 1


def min_subarray_sum(values: list[int]) -> int:
    best = curr = values[0]
    for v in values[1:]:
        curr = min(v, curr + v)
        best = min(best, curr)
    return best


def max_subarray_circular(values: list[int]) -> int:
    """Best slice when the array wraps around; slices stay non-empty."""
    if not values:
        raise ValueError("max_subarray_circular needs at least one element")
    straight = max_subarray_sum(values)
    if straight < 0:
        return straight  # every element negative, so no wrap can help
    return max(straight, sum(values) - min_subarray_sum(values))


def main() -> None:
    samples = [
        [-2, 1, -3, 4, -1, 2, 1, -5, 4],
        [5, 4, -1, 7, 8],
        [-3, -2, -8, -1],
        [1, -2, 3, -2],
        [3, -1, 2, -1],
        [-2, -3, -1],
    ]
    for values in samples:
        total, start, end = max_subarray(values)
        print(f"{values}")
        print(f"  best sum {total} from slice [{start}:{end}] = {values[start:end]}")
        assert sum(values[start:end]) == total == max_subarray_sum(values)
        print(f"  circular best: {max_subarray_circular(values)}")

    print("\nedge cases:")
    print("  single element:", max_subarray([7]))
    print("  all negative circular:", max_subarray_circular([-4, -2, -9]))
    print("  wrap beats straight:", max_subarray_circular([5, -3, 5]))
    try:
        max_subarray([])
    except ValueError as exc:
        print("  empty input:", exc)


if __name__ == "__main__":
    main()
