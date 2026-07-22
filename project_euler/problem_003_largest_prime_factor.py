"""Project Euler 3: largest prime factor of 600851475143.

Trial division is enough, given one insight: after dividing out every factor of
d, the remaining quotient has no factors below d. So divide n down as you go
and stop when d*d exceeds what is left — whatever remains above 1 at that point
is itself prime and is the largest factor.

That turns an O(n) scan into O(sqrt(n)) on the *shrinking* quotient, which for
600851475143 means a few thousand steps instead of 600 billion.

Answer: 6857.
"""


def prime_factors(n: int) -> list[int]:
    """Full factorisation with multiplicity, by shrinking trial division."""
    factors: list[int] = []
    for d in (2, 3):
        while n % d == 0:
            factors.append(d)
            n //= d
    d = 5
    while d * d <= n:  # d*d compares against the *reduced* n
        for step in (2, 4):  # 6k +/- 1 wheel: skips multiples of 2 and 3
            while n % d == 0:
                factors.append(d)
                n //= d
            d += step
    if n > 1:
        factors.append(n)  # what remains is prime
    return factors


def largest_prime_factor(n: int) -> int:
    return prime_factors(n)[-1]


def main() -> None:
    print(f"600851475143 = {' * '.join(map(str, prime_factors(600851475143)))}")
    print(f"largest prime factor: {largest_prime_factor(600851475143)}")

    print(f"13195 -> {prime_factors(13195)}")
    print(f"multiplicity kept: 360 -> {prime_factors(360)}")
    print(f"a prime factors to itself: 97 -> {prime_factors(97)}")
    print(f"2**20 -> {len(prime_factors(2**20))} twos")

    product = 1
    for f in prime_factors(600851475143):
        product *= f
    print(f"factors multiply back: {product == 600851475143}")

    semiprime = 999_999_000_001  # 999983 * 1000007, both prime
    print(f"large semiprime {semiprime} -> {prime_factors(semiprime)}")


if __name__ == "__main__":
    main()
