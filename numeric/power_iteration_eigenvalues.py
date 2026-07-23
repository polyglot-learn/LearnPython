"""Power iteration: find the dominant eigenpair by repeated multiplication.

Multiplying any starting vector by A repeatedly amplifies the component along
the eigenvector with the largest-magnitude eigenvalue faster than all the
others, so the normalised iterate converges to that dominant eigenvector. The
Rayleigh quotient v^T A v / v^T v then reads off the matching eigenvalue. Each
step is one matrix-vector product, O(n^2), and the error shrinks by the ratio
|lambda_2 / lambda_1| per iteration, so a large spectral gap means fast
convergence and a small gap means slow.

To reach the second eigenpair on a symmetric matrix, deflate: subtract
lambda_1 * v1 v1^T from A. That zeroes out the dominant direction while leaving
the rest of the spectrum untouched, so power iteration on the deflated matrix
surfaces the next eigenvalue. Every result is checked against the defining
equation A v = lambda v.
"""

Matrix = list[list[float]]
Vector = list[float]


def mat_vec(A: Matrix, v: Vector) -> Vector:
    return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]


def dot(a: Vector, b: Vector) -> float:
    return sum(x * y for x, y in zip(a, b))


def normalise(v: Vector) -> Vector:
    norm = dot(v, v) ** 0.5
    return [x / norm for x in v]


def power_iteration(A: Matrix, iterations: int = 1000,
                    tol: float = 1e-12) -> tuple[float, Vector]:
    """Return the dominant (eigenvalue, unit eigenvector) of A."""
    n = len(A)
    v = normalise([1.0 / (i + 1) for i in range(n)])  # asymmetric start
    lam = 0.0
    for _ in range(iterations):
        w = mat_vec(A, v)
        v_new = normalise(w)
        # Rayleigh quotient gives the eigenvalue estimate for the current v.
        lam_new = dot(v_new, mat_vec(A, v_new))
        # Fix sign: eigenvectors are defined up to a sign flip each step.
        if dot(v_new, v) < 0:
            v_new = [-x for x in v_new]
        if abs(lam_new - lam) < tol:
            return lam_new, v_new
        v, lam = v_new, lam_new
    return lam, v


def deflate(A: Matrix, lam: float, v: Vector) -> Matrix:
    """Remove the eigenpair (lam, v) from symmetric A: A - lam v v^T."""
    n = len(A)
    return [[A[i][j] - lam * v[i] * v[j] for j in range(n)] for i in range(n)]


def main() -> None:
    # Symmetric matrix with known eigenvalues 6, 3, 3 (from a textbook example).
    A: Matrix = [[4.0, 1.0, 1.0],
                 [1.0, 4.0, 1.0],
                 [1.0, 1.0, 4.0]]

    lam1, v1 = power_iteration(A)
    print(f"dominant eigenvalue: {lam1:.6f}  (expect 6)")
    print(f"  eigenvector: {[round(x, 4) for x in v1]}")
    av = mat_vec(A, v1)
    resid = max(abs(av[i] - lam1 * v1[i]) for i in range(len(A)))
    print(f"  max |A v - lambda v|: {resid:.2e}")

    lam2, v2 = power_iteration(deflate(A, lam1, v1))
    print(f"\nsecond eigenvalue (deflation): {lam2:.6f}  (expect 3)")
    av2 = mat_vec(A, v2)
    resid2 = max(abs(av2[i] - lam2 * v2[i]) for i in range(len(A)))
    print(f"  max |A v - lambda v| on original A: {resid2:.2e}")
    print(f"  v1 . v2 (orthogonal): {dot(v1, v2):.2e}")

    # 2x2 with clear gap: eigenvalues 5 and 2, converges fast.
    B: Matrix = [[4.0, 1.0], [2.0, 3.0]]
    lamB, vB = power_iteration(B)
    print(f"\n2x2 dominant eigenvalue: {lamB:.6f}  (expect 5)")
    avB = mat_vec(B, vB)
    print(f"  max |A v - lambda v|: "
          f"{max(abs(avB[i] - lamB * vB[i]) for i in range(2)):.2e}")


if __name__ == "__main__":
    main()
