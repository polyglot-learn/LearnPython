"""Finding the unpaired element with xor, in constant space.

Xor has three properties that together solve the problem: it is commutative and
associative, so the order of the input does not matter; x ^ x is 0, so a pair
cancels; and x ^ 0 is x, so the survivor is untouched. Fold xor over an array in
which every value appears twice except one, and everything paired annihilates,
leaving exactly the odd one out. One pass, no hash set, O(1) space.

The two-unpaired variant needs one more idea. The fold now yields a ^ b, the xor
of the two singles. That value is non-zero, so it has a lowest set bit, and by
construction the two singles differ at that position: one has it set and one
does not. Partitioning the array on that bit therefore separates a from b while
keeping every duplicate pair together in whichever half it falls, so folding xor
over each half independently recovers both.

The isolation idiom is x & -x, which keeps only the lowest set bit because -x is
~x + 1. Both routines are O(n) time and O(1) space, and neither needs the input
sorted or hashable beyond being an int.
"""

from functools import reduce
from operator import xor


def single_number(nums: list[int]) -> int:
    """Every value appears twice except one. Returns 0 for an empty list."""
    return reduce(xor, nums, 0)


def two_single_numbers(nums: list[int]) -> tuple[int, int]:
    """Every value appears twice except two distinct ones."""
    both = reduce(xor, nums, 0)
    if both == 0:
        raise ValueError("no two distinct unpaired values present")
    low = both & -both  # a bit where the two singles differ
    a = 0
    for n in nums:
        if n & low:
            a ^= n
    b = both ^ a
    return (a, b) if a <= b else (b, a)


def single_number_thrice(nums: list[int], width: int = 32) -> int:
    """Every value appears three times except one; count bits modulo three."""
    result = 0
    for i in range(width):
        column = sum(n >> i & 1 for n in nums) % 3
        result |= column << i
    sign = 1 << (width - 1)
    return result - (1 << width) if result & sign else result


def missing_number(nums: list[int]) -> int:
    """0..n with one value missing: xor the values against the full range."""
    n = len(nums)
    return reduce(xor, nums, 0) ^ reduce(xor, range(n + 1), 0)


def main() -> None:
    print(f"single_number([4,1,2,1,2]): {single_number([4, 1, 2, 1, 2])}")
    print(f"single_number([7]):         {single_number([7])}")
    print(f"single_number([]):          {single_number([])}")
    print(f"order does not matter:      {single_number([2, 1, 2, 1, 4])}")

    pair = [1, 2, 1, 3, 2, 5]
    print(f"\ntwo_single_numbers({pair}): {two_single_numbers(pair)}")
    print(f"two_single_numbers([1, 2]): {two_single_numbers([1, 2])}")
    big = [10 ** 9, 7, 10 ** 9, 8, 3, 3]
    print(f"large values: {two_single_numbers(big)}")
    try:
        two_single_numbers([1, 1, 2, 2])
    except ValueError as exc:
        print(f"all values paired: {exc}")

    print(f"\nthrice: {single_number_thrice([2, 2, 3, 2])}")
    print(f"thrice with negatives: {single_number_thrice([-2, -2, 1, -2])}")

    print(f"\nmissing_number([3, 0, 1]):    {missing_number([3, 0, 1])}")
    print(f"missing_number([0]):          {missing_number([0])}")
    print(f"missing_number([]):           {missing_number([])}")

    # Exhaustive check on a generated instance.
    data = [i for i in range(1, 500) for _ in range(2)] + [12345]
    print(f"\n500 pairs plus one single: {single_number(data)}")
    data2 = [i for i in range(1, 500) for _ in range(2)] + [12345, 999]
    print(f"same with two singles: {two_single_numbers(data2)}")


if __name__ == "__main__":
    main()
