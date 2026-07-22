"""Primality by trial division, sped up by only testing 6k +/- 1 candidates.

A composite n always has a divisor no larger than sqrt(n), because if both
factors were larger their product would exceed n. So testing divisors up to
sqrt(n) is enough, which turns an O(n) scan into O(sqrt(n)).

The second trick removes most of the remaining candidates. Every integer is
one of 6k, 6k+1, 6k+2, 6k+3, 6k+4, 6k+5. Of those, 6k, 6k+2 and 6k+4 are even
and 6k+3 is a multiple of 3, so after handling 2 and 3 by hand only 6k+1 and
6k+5 (equivalently 6k-1) can be prime. Stepping by 6 and testing two divisors
per step checks a third of the numbers a naive loop would.

This test is deterministic and never wrong, but sqrt(n) grows fast: for a
64-bit n it is billions of divisions. For anything large use Miller-Rabin.
"""


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True  # 2 and 3
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:  # i * i avoids a float sqrt and its rounding problems
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def is_prime_naive(n: int) -> bool:
    """The unoptimised version, kept for comparison."""
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def smallest_factor(n: int) -> int:
    """The least divisor above 1, which equals n itself when n is prime."""
    if n < 2:
        raise ValueError("smallest_factor is defined for n >= 2")
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    i = 5
    while i * i <= n:
        if n % i == 0:
            return i
        if n % (i + 2) == 0:
            return i + 2
        i += 6
    return n


def main() -> None:
    print(f"primes below 50: {[n for n in range(50) if is_prime(n)]}")

    for n in (-7, 0, 1, 2, 3, 4, 25, 97, 561, 7919):
        print(f"is_prime({n:5d}) = {is_prime(n)}")

    # The two implementations must agree everywhere.
    agree = all(is_prime(n) == is_prime_naive(n) for n in range(-5, 2000))
    print(f"optimised and naive agree on -5..1999: {agree}")

    print(f"smallest_factor(91)     = {smallest_factor(91)}")
    print(f"smallest_factor(97)     = {smallest_factor(97)}")
    print(f"smallest_factor(1000003) = {smallest_factor(1000003)}")

    # A large prime is still fine, but note the loop ran ~1e5 times for it.
    big = 1_000_000_007
    print(f"is_prime({big}) = {is_prime(big)}")


if __name__ == "__main__":
    main()
