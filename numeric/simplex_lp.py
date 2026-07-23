"""Simplex method: maximise a linear objective over a polytope of constraints.

A linear program in standard form maximises c.x subject to Ax <= b and x >= 0.
The feasible region is a convex polytope, and a linear objective always attains
its maximum at a vertex, so the search reduces to walking from vertex to
vertex. The simplex method does exactly that: it adds a slack variable per
constraint to turn inequalities into equalities, then repeatedly pivots to an
adjacent vertex that improves the objective.

Each pivot picks an entering variable with a favourable objective coefficient
and a leaving variable chosen by the minimum-ratio test, which keeps every
variable non-negative. When no entering column can improve the objective the
current vertex is optimal. This standard-form version assumes b >= 0 so the
origin is a feasible starting vertex; it is worst-case exponential but fast in
practice on the small problems here.
"""

Matrix = list[list[float]]


def simplex(c: list[float], A: Matrix, b: list[float]) -> tuple[float, list[float]]:
    """Maximise c.x s.t. Ax <= b, x >= 0. Returns (optimum, x). b >= 0."""
    m, n = len(A), len(c)
    # Tableau rows: constraints then the objective. Columns: x, slacks, rhs.
    table = [row[:] + [1.0 if j == i else 0.0 for j in range(m)] + [b[i]]
             for i, row in enumerate(A)]
    table.append([-ci for ci in c] + [0.0] * m + [0.0])
    basis = list(range(n, n + m))  # slacks are the initial basic variables

    while True:
        obj = table[-1]
        pivot_col = min(range(n + m), key=lambda j: obj[j])
        if obj[pivot_col] >= -1e-12:
            break  # no improving column: optimal
        # Minimum-ratio test over rows with a positive entry in the column.
        pivot_row, best_ratio = -1, float("inf")
        for i in range(m):
            if table[i][pivot_col] > 1e-12:
                ratio = table[i][-1] / table[i][pivot_col]
                if ratio < best_ratio:
                    best_ratio, pivot_row = ratio, i
        if pivot_row == -1:
            raise ValueError("problem is unbounded")
        _pivot(table, pivot_row, pivot_col)
        basis[pivot_row] = pivot_col

    x = [0.0] * n
    for i in range(m):
        if basis[i] < n:
            x[basis[i]] = table[i][-1]
    return table[-1][-1], x


def _pivot(table: Matrix, pr: int, pc: int) -> None:
    piv = table[pr][pc]
    table[pr] = [v / piv for v in table[pr]]
    for i in range(len(table)):
        if i != pr and abs(table[i][pc]) > 1e-15:
            factor = table[i][pc]
            table[i] = [a - factor * b for a, b in zip(table[i], table[pr])]


def main() -> None:
    # maximise 3x + 5y s.t. x <= 4, 2y <= 12, 3x + 2y <= 18, x,y >= 0.
    # Classic problem; optimum is 36 at the vertex (2, 6).
    c = [3.0, 5.0]
    A = [[1.0, 0.0], [0.0, 2.0], [3.0, 2.0]]
    b = [4.0, 12.0, 18.0]
    opt, x = simplex(c, A, b)
    print(f"optimum: {opt:.4f}  (expected 36)")
    print(f"vertex:  x={x[0]:.4f}, y={x[1]:.4f}  (expected 2, 6)")

    # A 3-variable LP: maximise 20a + 10b + 15c under three constraints.
    c2 = [20.0, 10.0, 15.0]
    A2 = [[3.0, 2.0, 5.0], [2.0, 1.0, 1.0], [1.0, 1.0, 3.0]]
    b2 = [55.0, 26.0, 30.0]
    opt2, x2 = simplex(c2, A2, b2)
    print(f"3-var optimum: {opt2:.4f}")
    print(f"3-var vertex:  {[round(v, 4) for v in x2]}")
    # Verify feasibility of the returned vertex.
    feasible = all(sum(A2[i][j] * x2[j] for j in range(3)) <= b2[i] + 1e-9
                   for i in range(3))
    print(f"vertex satisfies all constraints: {feasible}")

    # Unboundedness is detected, not silently wrong.
    try:
        simplex([1.0], [[-1.0]], [0.0])
    except ValueError as e:
        print(f"detected: {e}")


if __name__ == "__main__":
    main()
