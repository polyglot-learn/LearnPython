"""Miller-Rabin: a fast primality test, made deterministic for 64-bit inputs.

The test builds on two facts about a prime p. Fermat's little theorem gives
a**(p-1) == 1 (mod p) for any a not divisible by p. And modulo a prime the
only square roots of 1 are 1 and -1, because x**2 - 1 factors as
(x-1)(x+1) and a prime dividing a product must divide one of the factors.

So write n - 1 as d * 2**s with d odd, and compute a**d, then square it s
times. For a prime the sequence must arrive at 1, and the step just before the
first 1 must be -1. If instead you see a 1 arrive from something that is
neither 1 nor -1, you have found a nontrivial square root of 1 and n is
certainly composite. A base a that proves this is called a witness.

Picking bases at random makes the test probabilistic, but for n below
3.3 * 10**24 the fixed base set {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}
has been verified to contain a witness for every composite, so testing exactly
those twelve bases is deterministic for anything a 64-bit integer can hold.
Cost is O(k log^3 n) bit operations for k bases, which is far below the
sqrt(n) of trial division.
"""

# Verified sufficient for every n < 3,317,044,064,679,887,385,961,981.
WITNESSES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_composite_witness(n: int, a: int, d: int, s: int) -> bool:
    """True if base a proves n composite; False if a says nothing."""
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return False  # consistent with n being prime
    for _ in range(s - 1):
        x = x * x % n
        if x == n - 1:
            return False  # reached -1, so the remaining squarings give 1
    return True  # arrived at 1 (or never reached -1) from a bad root


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in WITNESSES:
        if n % p == 0:
            return n == p  # catches the small primes themselves
    # Factor out the powers of two from n - 1.
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    return not any(is_composite_witness(n, a, d, s) for a in WITNESSES)


def next_prime(n: int) -> int:
    """The smallest prime strictly greater than n."""
    candidate = max(n + 1, 2)
    if candidate > 2 and candidate % 2 == 0:
        candidate += 1
    while not is_prime(candidate):
        candidate += 1 if candidate == 2 else 2
    return candidate


def trial_division(n: int) -> bool:
    """Slow but obviously correct, used here to cross-check Miller-Rabin."""
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def main() -> None:
    print(f"primes below 40: {[n for n in range(40) if is_prime(n)]}")

    for n in (0, 1, 2, 561, 7919, 1_000_000_007, 2**61 - 1, 2**64 - 59):
        print(f"is_prime({n}) = {is_prime(n)}")

    # 561 and 41041 are Carmichael numbers: composite, yet they pass the plain
    # Fermat test for every base coprime to them. Miller-Rabin is not fooled.
    for n in (561, 1105, 1729, 2465, 41041):
        fermat_says = pow(2, n - 1, n) == 1
        print(f"n={n:6d}  fermat base 2 says prime: {fermat_says}, "
              f"miller-rabin: {is_prime(n)}")

    agree = all(is_prime(n) == trial_division(n) for n in range(20_000))
    print(f"agrees with trial division below 20000: {agree}")

    print(f"next_prime(1) = {next_prime(1)}")
    print(f"next_prime(2**60) = {next_prime(2**60)}")


if __name__ == "__main__":
    main()
