"""LU decomposition: factor once, then solve many systems cheaply.

Gaussian elimination on A can be recorded as a factorisation PA = LU, where L
is unit lower-triangular (the multipliers used to eliminate), U is upper-
triangular (the result), and P is the permutation from partial pivoting. The
factoring costs O(n^3), the same as one elimination, but it is done only once.

The payoff is reuse. To solve Ax = b, permute b, then solve Ly = Pb by forward
substitution and Ux = y by back substitution, each O(n^2). So a second, third,
or hundredth right-hand side costs only O(n^2) instead of redoing the cubic
work every time, which is exactly what matrix inversion and many-column solves
need. Pivoting keeps the factorisation numerically stable, and PA = LU can be
checked entry by entry to confirm the decomposition is correct.
"""

Matrix = list[list[float]]
Vector = list[float]


def lu_decompose(A: Matrix) -> tuple[Matrix, Matrix, list[int]]:
    """Return L, U, and the permutation perm with A[perm] == L @ U."""
    n = len(A)
    U = [row[:] for row in A]
    L = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    perm = list(range(n))
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(U[r][col]))
        if abs(U[pivot][col]) < 1e-12:
            raise ValueError("matrix is singular")
        if pivot != col:
            U[col], U[pivot] = U[pivot], U[col]
            perm[col], perm[pivot] = perm[pivot], perm[col]
            # Swap the already-computed part of L to match the row swap.
            for k in range(col):
                L[col][k], L[pivot][k] = L[pivot][k], L[col][k]
        for r in range(col + 1, n):
            factor = U[r][col] / U[col][col]
            L[r][col] = factor
            for k in range(col, n):
                U[r][k] -= factor * U[col][k]
    return L, U, perm


def lu_solve(L: Matrix, U: Matrix, perm: list[int], b: Vector) -> Vector:
    """Solve Ax = b reusing a factorisation; O(n^2) per right-hand side."""
    n = len(L)
    pb = [b[perm[i]] for i in range(n)]
    y = [0.0] * n
    for i in range(n):  # forward substitution: Ly = Pb
        y[i] = pb[i] - sum(L[i][j] * y[j] for j in range(i))
    x = [0.0] * n
    for i in range(n - 1, -1, -1):  # back substitution: Ux = y
        x[i] = (y[i] - sum(U[i][j] * x[j] for j in range(i + 1, n))) / U[i][i]
    return x


def main() -> None:
    A = [[2.0, 1.0, 1.0], [4.0, -6.0, 0.0], [-2.0, 7.0, 2.0]]
    L, U, perm = lu_decompose(A)

    # Verify PA == LU entry by entry.
    n = len(A)
    lu = [[sum(L[i][k] * U[k][j] for k in range(n)) for j in range(n)]
          for i in range(n)]
    pa = [A[perm[i]] for i in range(n)]
    max_diff = max(abs(lu[i][j] - pa[i][j]) for i in range(n) for j in range(n))
    print(f"max |PA - LU|: {max_diff:.2e}")

    # Solve for three different right-hand sides reusing one factorisation.
    for b in ([5.0, -2.0, 9.0], [1.0, 0.0, 0.0], [3.0, 3.0, 3.0]):
        x = lu_solve(L, U, perm, b)
        residual = [sum(A[i][j] * x[j] for j in range(n)) - b[i]
                    for i in range(n)]
        print(f"b={b} -> x={[round(v, 4) for v in x]}, "
              f"residual {max(abs(r) for r in residual):.1e}")

    # Larger random system, many solves: confirm each solution.
    import random

    rng = random.Random(1)
    m = 15
    M = [[rng.uniform(-4, 4) for _ in range(m)] for _ in range(m)]
    Lm, Um, pm = lu_decompose(M)
    worst = 0.0
    for _ in range(10):
        true_x = [rng.uniform(-4, 4) for _ in range(m)]
        rhs = [sum(M[i][j] * true_x[j] for j in range(m)) for i in range(m)]
        got = lu_solve(Lm, Um, pm, rhs)
        worst = max(worst, max(abs(got[i] - true_x[i]) for i in range(m)))
    print(f"15x15, 10 right-hand sides, max error: {worst:.2e}")


if __name__ == "__main__":
    main()
