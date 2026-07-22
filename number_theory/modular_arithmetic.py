"""Arithmetic modulo m: addition, multiplication, powers, and division.

Working modulo m means keeping only the remainder after dividing by m.
Addition and multiplication survive the reduction unchanged, so you may reduce
whenever you like, which is what keeps intermediate values small.

Division is the interesting one. There is no "divide by 3" modulo m; instead
you multiply by the modular inverse of 3, the number x with 3x == 1 (mod m).
That inverse exists exactly when gcd(3, m) == 1, because the extended
Euclidean algorithm can then write 3x + my = 1, and reducing modulo m leaves
3x == 1. When m is prime there is a second route: Fermat's little theorem says
a**(m-1) == 1 for any a not divisible by m, so a**(m-2) is the inverse. Euclid
is O(log m) and works for any modulus; Fermat is O(log m) modular multiplies
and needs a prime modulus, but is a one-liner with pow().

Python's % is worth knowing precisely: the result always takes the sign of the
divisor, so (-7) % 3 is 2, not -1. That is the mathematically conventional
representative and means no manual sign fixing is ever needed.
"""


def add_mod(a: int, b: int, m: int) -> int:
    return (a + b) % m


def sub_mod(a: int, b: int, m: int) -> int:
    return (a - b) % m  # Python's % already returns a non-negative result


def mul_mod(a: int, b: int, m: int) -> int:
    return a * b % m


def pow_mod(a: int, e: int, m: int) -> int:
    """Square-and-multiply, keeping every intermediate below m squared."""
    result, a = 1, a % m
    while e > 0:
        if e & 1:
            result = result * a % m
        a = a * a % m
        e >>= 1
    return result


def inverse_euclid(a: int, m: int) -> int:
    """The x with a*x == 1 (mod m), for any m coprime to a."""
    if m <= 1:
        raise ValueError("modulus must be greater than 1")
    old_r, r = a % m, m
    old_x, x = 1, 0
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_x, x = x, old_x - q * x
    if old_r != 1:
        raise ValueError(f"{a} has no inverse modulo {m}")
    return old_x % m


def inverse_fermat(a: int, p: int) -> int:
    """The inverse modulo a prime p, as a**(p-2). Wrong if p is not prime."""
    a %= p
    if a == 0:
        raise ValueError("0 has no inverse")
    return pow(a, p - 2, p)


def divide_mod(a: int, b: int, m: int) -> int:
    """a / b modulo m, meaning a times the inverse of b."""
    return a * inverse_euclid(b, m) % m


def main() -> None:
    m = 1_000_000_007
    print(f"add_mod(999999999, 999999999, {m}) = {add_mod(999999999, 999999999, m)}")
    print(f"mul_mod(123456789, 987654321, {m}) = {mul_mod(123456789, 987654321, m)}")
    print(f"pow_mod(2, 1000, {m})              = {pow_mod(2, 1000, m)}")
    print(f"pow(2, 1000, {m})                  = {pow(2, 1000, m)}")

    # The sign convention: % follows the divisor, so results are never negative.
    print(f"(-7) % 3    = {(-7) % 3}")
    print(f"sub_mod(2, 5, 3) = {sub_mod(2, 5, 3)}")

    inv = inverse_euclid(3, 11)
    print(f"inverse of 3 mod 11 = {inv}, check 3*{inv} % 11 = {3 * inv % 11}")

    inv_e = inverse_euclid(123456789, m)
    inv_f = inverse_fermat(123456789, m)
    print(f"inverse of 123456789 mod 1e9+7: euclid {inv_e}, fermat {inv_f}")
    print(f"both agree: {inv_e == inv_f}")

    print(f"divide_mod(10, 4, 13) = {divide_mod(10, 4, 13)} "
          f"(check: 4 * that = {4 * divide_mod(10, 4, 13) % 13})")

    # 4 and 6 share the factor 2, so no inverse exists modulo 6.
    try:
        inverse_euclid(4, 6)
    except ValueError as exc:
        print(f"expected failure: {exc}")

    ok = all(a * inverse_euclid(a, 17) % 17 == 1 for a in range(1, 17))
    print(f"every nonzero residue mod 17 is invertible: {ok}")


if __name__ == "__main__":
    main()
