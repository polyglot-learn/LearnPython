"""Powers of two: testing, rounding up, and reading the exponent off bit_length.

A positive power of two is exactly a number with a single set bit. Since n - 1
clears that bit and sets every bit below it, n & (n - 1) is zero precisely when
n had at most one set bit. Guarding with n > 0 rules out zero and negatives, and
the test is then a single comparison rather than a loop or a logarithm.

Rounding up to the next power of two follows from bit_length(), which is the
position of the highest set bit plus one. For a value that is already a power of
two the answer is the value itself; otherwise it is 1 << bit_length(n). Writing
it as 1 << (n - 1).bit_length() handles both cases at once, because subtracting
one drops an exact power down a bit-length.

The exponent itself is bit_length() - 1, and n.bit_length() also gives a cheap
integer floor of log2 with none of the rounding hazards that math.log2 has on
large integers.

All operations are O(1) in machine words and exact for arbitrarily large ints.
"""

import math


def is_power_of_two(n: int) -> bool:
    return n > 0 and n & (n - 1) == 0


def next_power_of_two(n: int) -> int:
    """Smallest power of two >= n; returns 1 for n <= 1."""
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()


def previous_power_of_two(n: int) -> int:
    """Largest power of two <= n; undefined for n < 1."""
    if n < 1:
        raise ValueError("no power of two is <= 0")
    return 1 << (n.bit_length() - 1)


def exponent(n: int) -> int | None:
    return n.bit_length() - 1 if is_power_of_two(n) else None


def floor_log2(n: int) -> int:
    if n < 1:
        raise ValueError("log2 needs a positive int")
    return n.bit_length() - 1


def main() -> None:
    for n in [0, 1, 2, 3, 4, 6, 16, 31, 32, 1024, 1025, -8]:
        print(f"{n:>6}: power_of_two={is_power_of_two(n)!s:<5} "
              f"exponent={exponent(n)}")

    print()
    for n in [0, 1, 2, 3, 5, 17, 64, 65, 1000]:
        print(f"next_power_of_two({n}) = {next_power_of_two(n)}")

    print()
    for n in [1, 2, 3, 5, 17, 64, 65, 1000]:
        print(f"previous_power_of_two({n}) = {previous_power_of_two(n)}")

    checks = all(
        (next_power_of_two(n) >= n and is_power_of_two(next_power_of_two(n))
         and next_power_of_two(n) // 2 < max(n, 1))
        for n in range(1, 2000)
    )
    print(f"\nnext_power_of_two is tight and correct for 1..1999: {checks}")

    # bit_length beats math.log2 on large integers, which loses precision.
    big = (1 << 53) - 1  # just under a power of two, past float's exact range
    print(f"\nfloor_log2({big}) = {floor_log2(big)}")
    print(f"int(math.log2(big)) = {int(math.log2(big))} (float rounds it up)")
    huge = 1 << 5000
    print(f"floor_log2(1 << 5000) = {floor_log2(huge)}")
    # math.log2 handles big ints, but it returns a float, so anything past 2^53
    # is a rounded answer rather than an exact one.
    print(f"math.log2(1 << 5000) = {math.log2(huge)}")
    off_by_one = sum(
        1 for k in range(50, 70) if int(math.log2((1 << k) - 1)) != k - 1
    )
    print(f"int(math.log2(2^k - 1)) is wrong for {off_by_one} of k in 50..69")

    print(f"\nis_power_of_two(1 << 5000): {is_power_of_two(huge)}")
    try:
        previous_power_of_two(0)
    except ValueError as exc:
        print(f"previous_power_of_two(0): {exc}")


if __name__ == "__main__":
    main()
