"""Gaussian elimination over GF(2) and over a prime field.

Solving a linear system by row reduction is the same over a finite field as
over the reals, with one simplification: there is no rounding, so the answer is
exact. Over GF(2) every operation is XOR, which makes the whole solver a few
bitwise lines and is the engine behind linear cryptanalysis, error-correcting
codes, and the linear-algebra stage of modern factoring.

The method: for each column find a pivot row, swap it up, and eliminate that
column from every other row. Over a prime field p, "divide by the pivot" means
multiply by its modular inverse. The rank tells you whether the system is
uniquely solvable, underdetermined, or inconsistent.

O(n^3) field operations for an n by n system.
"""


def solve_gf2(matrix: list[int], constants: list[int], num_vars: int) -> list[int] | None:
    """Solve Ax = b over GF(2). Rows of A are packed into ints (bit j = column j)."""
    rows = [row | (c << num_vars) for row, c in zip(matrix, constants)]
    pivot_row = 0
    where = [-1] * num_vars
    for col in range(num_vars):
        sel = next((r for r in range(pivot_row, len(rows)) if rows[r] >> col & 1), None)
        if sel is None:
            continue
        rows[pivot_row], rows[sel] = rows[sel], rows[pivot_row]
        for r in range(len(rows)):
            if r != pivot_row and rows[r] >> col & 1:
                rows[r] ^= rows[pivot_row]  # elimination is just XOR
        where[col] = pivot_row
        pivot_row += 1

    for r in range(pivot_row, len(rows)):
        if rows[r] >> num_vars & 1:  # 0 = 1 -> inconsistent
            return None
    return [(rows[where[c]] >> num_vars & 1) if where[c] != -1 else 0 for c in range(num_vars)]


def solve_mod_p(a: list[list[int]], b: list[int], p: int) -> list[int] | None:
    """Solve Ax = b over the field of integers mod prime p. Assumes a unique solution."""
    n = len(a)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]  # augmented matrix
    for col in range(n):
        pivot = next((r for r in range(col, n) if m[r][col] % p), None)
        if pivot is None:
            return None  # singular
        m[col], m[pivot] = m[pivot], m[col]
        inv = pow(m[col][col], p - 2, p)  # Fermat inverse of the pivot
        m[col] = [(x * inv) % p for x in m[col]]
        for r in range(n):
            if r != col and m[r][col]:
                factor = m[r][col]
                m[r] = [(m[r][k] - factor * m[col][k]) % p for k in range(n + 1)]
    return [m[i][n] % p for i in range(n)]


def main() -> None:
    # GF(2): 3 equations, 3 unknowns.
    # x0 ^ x1     = 1
    #      x1 ^ x2 = 0
    # x0      ^ x2 = 1
    matrix = [0b011, 0b110, 0b101]  # bit j is column j
    constants = [1, 0, 1]
    solution = solve_gf2(matrix, constants, 3)
    print(f"GF(2) solution: {solution}")
    for row, c in zip(matrix, constants):
        got = bin(row & int("".join(map(str, reversed(solution))), 2)).count("1") % 2
        print(f"  equation {row:03b} = {c}: satisfied = {got == c}")

    print("inconsistent system returns None:")
    print(f"  {solve_gf2([0b01, 0b01], [0, 1], 2)}")

    # Over GF(7): 2x + 3y = 5, 4x + y = 6.
    print("mod-7 system 2x+3y=5, 4x+y=6:")
    sol = solve_mod_p([[2, 3], [4, 1]], [5, 6], 7)
    print(f"  x, y = {sol}")
    if sol:
        x, y = sol
        print(f"  check: 2x+3y mod 7 = {(2 * x + 3 * y) % 7}, "
              f"4x+y mod 7 = {(4 * x + y) % 7}")

    # A larger random mod-p system, cross-checked by substitution.
    import random

    rng = random.Random(0)
    p = 101
    n = 5
    x_true = [rng.randrange(p) for _ in range(n)]
    a = [[rng.randrange(p) for _ in range(n)] for _ in range(n)]
    b = [sum(a[i][j] * x_true[j] for j in range(n)) % p for i in range(n)]
    recovered = solve_mod_p(a, b, p)
    print(f"random 5x5 mod-{p} system recovered exactly: {recovered == x_true}")


if __name__ == "__main__":
    main()
