"""The Chinese remainder theorem: rebuild a number from its remainders.

Given x == a1 (mod m1), x == a2 (mod m2), and so on with the moduli pairwise
coprime, there is exactly one solution modulo the product M of all the moduli.
Knowing the remainders is therefore equivalent to knowing the number itself,
as long as it is smaller than M.

The construction is direct. For each congruence let M_i = M / m_i. Since the
moduli are coprime, M_i is invertible modulo m_i; call that inverse n_i. Then
the term a_i * M_i * n_i is congruent to a_i modulo m_i, because M_i * n_i is
1 there, and congruent to 0 modulo every other m_j, because m_j divides M_i.
Adding all the terms therefore matches every congruence at once, and reducing
modulo M gives the unique representative in the range 0 to M-1.

Uniqueness follows because two solutions differ by a multiple of every m_i,
hence of M. Cost is O(k log M) using the extended Euclidean algorithm for the
inverses. This is what lets big computations be split across several small
moduli and recombined, which is how large-integer libraries and some RSA
implementations get their speed.
"""


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    old_r, r = a, b
    old_x, x = 1, 0
    old_y, y = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_x, x = x, old_x - q * x
        old_y, y = y, old_y - q * y
    return old_r, old_x, old_y


def modular_inverse(a: int, m: int) -> int:
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} is not invertible modulo {m}")
    return x % m


def crt(remainders: list[int], moduli: list[int]) -> tuple[int, int]:
    """Solve the system for pairwise coprime moduli; return (x, M)."""
    if len(remainders) != len(moduli):
        raise ValueError("need one remainder per modulus")
    if not moduli:
        return 0, 1  # the empty system is satisfied by everything mod 1
    if any(m < 1 for m in moduli):
        raise ValueError("moduli must be positive")

    total_modulus = 1
    for m in moduli:
        total_modulus *= m

    result = 0
    for a, m in zip(remainders, moduli):
        partial = total_modulus // m
        # modular_inverse raises here if this modulus shares a factor with
        # another one, which is exactly the case the theorem excludes.
        result += a * partial * modular_inverse(partial, m)
    return result % total_modulus, total_modulus


def crt_pair(a1: int, m1: int, a2: int, m2: int) -> tuple[int, int]:
    """Merge two congruences, allowing moduli that share a factor.

    Solvable only when the remainders agree modulo gcd(m1, m2); the combined
    modulus is then lcm(m1, m2) rather than the product.
    """
    g, p, _ = extended_gcd(m1, m2)
    if (a2 - a1) % g != 0:
        raise ValueError("the congruences contradict each other")
    lcm = m1 // g * m2
    shift = (a2 - a1) // g * p % (m2 // g)
    return (a1 + m1 * shift) % lcm, lcm


def main() -> None:
    # The classic puzzle: a count that leaves 2 mod 3, 3 mod 5, 2 mod 7.
    x, m = crt([2, 3, 2], [3, 5, 7])
    print(f"x == {x} (mod {m})")
    print(f"  checks: {x % 3}, {x % 5}, {x % 7}")

    x, m = crt([1, 4, 6], [3, 5, 7])
    print(f"x == {x} (mod {m}), checks {x % 3}, {x % 5}, {x % 7}")

    # Edge cases: a single congruence, the empty system, and a modulus of 1.
    print(f"single: {crt([4], [7])}")
    print(f"empty:  {crt([], [])}")
    print(f"mod 1:  {crt([0], [1])}")

    # Non-coprime moduli are outside the theorem's hypothesis.
    try:
        crt([1, 2], [4, 6])
    except ValueError as exc:
        print(f"rejected non-coprime moduli: {exc}")

    # The pairwise merge handles them when the remainders are consistent.
    print(f"crt_pair(2, 4, 8, 6)  = {crt_pair(2, 4, 8, 6)}")
    try:
        crt_pair(1, 4, 2, 6)
    except ValueError as exc:
        print(f"contradiction: {exc}")

    # Every residue below the product is recovered from its remainders.
    ok = all(crt([n % 3, n % 5, n % 7], [3, 5, 7])[0] == n
             for n in range(105))
    print(f"round trip for every n below 105: {ok}")


if __name__ == "__main__":
    main()
