"""Binary exponentiation: compute base**exp with about log2(exp) multiplies.

Multiplying by base exp times is O(exp). The shortcut uses the binary
expansion of the exponent. Since base**(2k) == (base**k)**2, squaring doubles
the exponent for one multiplication, so any exponent can be reached by
repeatedly squaring and multiplying in the factor whenever the corresponding
bit of exp is set. That is O(log exp) multiplications instead of O(exp).

The modular version is the one that matters in practice. Reducing modulo m
after every multiplication keeps operands bounded by m, which is what makes
RSA, Diffie-Hellman and the Miller-Rabin primality test feasible. Without the
reduction the intermediate numbers would have millions of digits.

Python's built-in pow(base, exp, mod) does exactly this in C and should be
what you actually call; the code here is to show the mechanism.
"""


def power_iterative(base: int, exp: int) -> int:
    if exp < 0:
        raise ValueError("use floats for negative exponents")
    result = 1
    while exp:
        if exp & 1:  # this bit of the exponent is set, so fold in the factor
            result *= base
        base *= base
        exp >>= 1
    return result


def power_recursive(base: int, exp: int) -> int:
    if exp < 0:
        raise ValueError("use floats for negative exponents")
    if exp == 0:
        return 1
    half = power_recursive(base, exp // 2)
    if exp % 2:
        return half * half * base
    return half * half


def power_mod(base: int, exp: int, mod: int) -> int:
    """base**exp % mod with every intermediate kept below mod squared."""
    if mod <= 0:
        raise ValueError("modulus must be positive")
    if exp < 0:
        raise ValueError("negative exponents need a modular inverse")
    result = 1
    base %= mod
    while exp:
        if exp & 1:
            result = result * base % mod
        base = base * base % mod
        exp >>= 1
    return result


def multiply_mod(a: int, b: int, mod: int) -> int:
    """a * b % mod by doubling, the same trick applied to multiplication."""
    result = 0
    a %= mod
    while b > 0:
        if b & 1:
            result = (result + a) % mod
        a = (a + a) % mod
        b >>= 1
    return result


def main() -> None:
    print(f"power_iterative(2, 10) = {power_iterative(2, 10)}")
    print(f"power_recursive(2, 10) = {power_recursive(2, 10)}")
    print(f"2 ** 10                = {2 ** 10}")

    print(f"3 ** 0   = {power_iterative(3, 0)}")
    print(f"0 ** 0   = {power_iterative(0, 0)}")
    print(f"(-2) ** 5 = {power_iterative(-2, 5)}")

    print(f"power_mod(2, 100, 1_000_000_007) = "
          f"{power_mod(2, 100, 1_000_000_007)}")
    print(f"pow(2, 100, 1_000_000_007)       = {pow(2, 100, 1_000_000_007)}")
    print(f"power_mod(7, 0, 5) = {power_mod(7, 0, 5)}")
    print(f"power_mod(5, 3, 1) = {power_mod(5, 3, 1)}")

    # A 1000-bit exponent finishes instantly with reduction, and would not
    # otherwise: 2 ** (10 ** 6) alone has over 300,000 digits.
    huge = power_mod(3, 2**1000, 1_000_000_007)
    print(f"3 ** 2**1000 mod 1e9+7 = {huge}")

    print(f"multiply_mod(123456789, 987654321, 1_000_000_007) = "
          f"{multiply_mod(123456789, 987654321, 1_000_000_007)}")

    ok = all(power_mod(b, e, 97) == pow(b, e, 97)
             for b in range(20) for e in range(20))
    print(f"agrees with pow() on a small grid: {ok}")


if __name__ == "__main__":
    main()
