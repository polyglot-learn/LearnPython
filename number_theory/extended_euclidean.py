"""Extended Euclid: the gcd of a and b, plus the x and y with ax + by = g.

Ordinary Euclid throws away information. At every step it replaces (a, b) with
(b, a % b); the extended version also tracks how the current remainder is
built out of the original a and b. Keep each remainder r as r = a*x + b*y and
the same subtraction that updates the remainders updates the coefficients, so
when the remainder reaches the gcd its coefficients are the answer. The cost
is unchanged: O(log min(a, b)) steps.

This is the workhorse behind modular inverses. If gcd(a, m) == 1 then
ax + my = 1, and reducing modulo m gives ax == 1, so x is the inverse of a.

It also solves linear Diophantine equations ax + by = c in integers. Bezout's
identity says the achievable values of ax + by are exactly the multiples of g,
so a solution exists precisely when g divides c; scaling the base solution by
c // g gives one, and the general solution shifts x by b//g and y by -a//g,
which is why there are infinitely many or none at all.
"""


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (g, x, y) with a*x + b*y == g == gcd(a, b)."""
    old_r, r = a, b
    old_x, x = 1, 0
    old_y, y = 0, 1
    while r != 0:
        q = old_r // r
        # Every pair updates by the same rule, which preserves the invariant
        # old_r == a*old_x + b*old_y at all times.
        old_r, r = r, old_r - q * r
        old_x, x = x, old_x - q * x
        old_y, y = y, old_y - q * y
    return old_r, old_x, old_y


def modular_inverse(a: int, m: int) -> int:
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} and {m} are not coprime, so no inverse exists")
    return x % m


def solve_diophantine(a: int, b: int, c: int) -> tuple[int, int]:
    """One integer solution of a*x + b*y == c, or ValueError if none exists."""
    if a == 0 and b == 0:
        if c != 0:
            raise ValueError("0 = c has no solution unless c is 0")
        return 0, 0
    g, x, y = extended_gcd(a, b)
    if c % g != 0:
        raise ValueError(f"gcd({a}, {b}) = {g} does not divide {c}")
    factor = c // g
    return x * factor, y * factor


def diophantine_family(a: int, b: int, c: int, k: int) -> tuple[int, int]:
    """The k-th solution: shifting x by b//g is cancelled by shifting y."""
    x, y = solve_diophantine(a, b, c)
    g, _, _ = extended_gcd(a, b)
    return x + k * (b // g), y - k * (a // g)


def main() -> None:
    for a, b in [(240, 46), (35, 15), (17, 5), (0, 5), (7, 0)]:
        g, x, y = extended_gcd(a, b)
        print(f"gcd({a}, {b}) = {g} = {a}*({x}) + {b}*({y}) "
              f"-> {a * x + b * y}")

    print(f"inverse of 3 mod 26 = {modular_inverse(3, 26)}")
    print(f"inverse of 17 mod 3120 = {modular_inverse(17, 3120)}")

    x, y = solve_diophantine(25, 15, 35)
    print(f"25x + 15y = 35 -> x={x}, y={y}, check {25 * x + 15 * y}")

    for k in range(-2, 3):
        x, y = diophantine_family(25, 15, 35, k)
        print(f"  k={k:2d}: x={x:4d}, y={y:5d}, check {25 * x + 15 * y}")

    # 6x + 4y is always even, so it can never equal 7.
    try:
        solve_diophantine(6, 4, 7)
    except ValueError as exc:
        print(f"no solution: {exc}")

    ok = all(extended_gcd(a, b)[1] * a + extended_gcd(a, b)[2] * b
             == extended_gcd(a, b)[0]
             for a in range(1, 60) for b in range(1, 60))
    print(f"Bezout identity holds across a small grid: {ok}")


if __name__ == "__main__":
    main()
