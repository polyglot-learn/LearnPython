"""Rotate an array by k positions — the reversal trick, in O(1) space.

Reverse the whole array, then reverse each of the two pieces:

    [1 2 3 4 5 6 7], k=3
    reverse all      -> [7 6 5 4 3 2 1]
    reverse [0:k]    -> [5 6 7 | 4 3 2 1]
    reverse [k:]     -> [5 6 7 | 1 2 3 4]

O(n) time with 2n swaps, O(1) space. The slicing one-liner is clearer but
allocates a second array.
"""


def rotate_right(values: list[int], k: int) -> list[int]:
    a = list(values)
    n = len(a)
    if n == 0:
        return a
    k %= n  # rotating by n is a no-op; handles k > n and k < 0
    _reverse(a, 0, n - 1)
    _reverse(a, 0, k - 1)
    _reverse(a, k, n - 1)
    return a


def _reverse(a: list[int], lo: int, hi: int) -> None:
    while lo < hi:
        a[lo], a[hi] = a[hi], a[lo]
        lo += 1
        hi -= 1


def rotate_right_slicing(values: list[int], k: int) -> list[int]:
    if not values:
        return []
    k %= len(values)
    return values[-k:] + values[:-k] if k else list(values)


def rotate_left(values: list[int], k: int) -> list[int]:
    return rotate_right(values, -k)


def main() -> None:
    data = [1, 2, 3, 4, 5, 6, 7]
    print(f"right 3 -> {rotate_right(data, 3)}")
    print(f"slicing -> {rotate_right_slicing(data, 3)}")
    print(f"left 2  -> {rotate_left(data, 2)}")
    print(f"k > n   -> {rotate_right(data, 10)}")
    print(f"k = 0   -> {rotate_right(data, 0)}")
    # The standard library's deque rotates in place, in C.
    from collections import deque

    d = deque(data)
    d.rotate(3)
    print(f"deque   -> {list(d)}")


if __name__ == "__main__":
    main()
