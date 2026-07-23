"""Natural cubic spline: a smooth curve through every data point.

A cubic spline lays a separate cubic polynomial on each interval between knots
and glues them so that the value, first derivative and second derivative all
match at every interior knot. That continuity of the second derivative is what
makes the curve look smooth to the eye, unlike connecting the dots with straight
lines. The "natural" boundary sets the second derivative to zero at both ends.

The unknowns are the second derivatives at the knots. Matching the slopes on
both sides of each interior knot gives one equation per interior point, and the
system is tridiagonal, so it solves in O(n) with the Thomas algorithm rather
than O(n^3) for a general solve. Once the second derivatives are known, each
piece is a cubic evaluated in closed form. The result interpolates exactly: it
passes through every knot, which is verified below, and it is far smoother than
piecewise-linear interpolation over the same points.
"""

Vector = list[float]


def solve_tridiagonal(sub: Vector, diag: Vector, sup: Vector,
                      rhs: Vector) -> Vector:
    """Thomas algorithm for a tridiagonal system; O(n)."""
    n = len(diag)
    c = sup[:]
    d = rhs[:]
    c[0] /= diag[0]
    d[0] /= diag[0]
    for i in range(1, n):
        denom = diag[i] - sub[i] * c[i - 1]
        c[i] = (sup[i] / denom) if i < n - 1 else 0.0
        d[i] = (d[i] - sub[i] * d[i - 1]) / denom
    x = [0.0] * n
    x[-1] = d[-1]
    for i in range(n - 2, -1, -1):
        x[i] = d[i] - c[i] * x[i + 1]
    return x


class CubicSpline:
    """Natural cubic spline over strictly increasing x samples."""

    def __init__(self, xs: Vector, ys: Vector) -> None:
        self.xs = xs
        self.ys = ys
        n = len(xs)
        h = [xs[i + 1] - xs[i] for i in range(n - 1)]
        # Build the tridiagonal system for second derivatives m[i].
        sub = [0.0] * n
        diag = [1.0] * n  # natural ends: m[0] = m[n-1] = 0
        sup = [0.0] * n
        rhs = [0.0] * n
        for i in range(1, n - 1):
            sub[i] = h[i - 1]
            diag[i] = 2.0 * (h[i - 1] + h[i])
            sup[i] = h[i]
            rhs[i] = 6.0 * ((ys[i + 1] - ys[i]) / h[i]
                            - (ys[i] - ys[i - 1]) / h[i - 1])
        self.m = solve_tridiagonal(sub, diag, sup, rhs)
        self.h = h

    def __call__(self, x: float) -> float:
        xs, ys, m, h = self.xs, self.ys, self.m, self.h
        # Locate the interval containing x (clamped at the ends).
        i = 0
        while i < len(h) - 1 and x > xs[i + 1]:
            i += 1
        dx = x - xs[i]
        hi = h[i]
        a = (xs[i + 1] - x) / hi
        b = dx / hi
        return (a * ys[i] + b * ys[i + 1]
                + ((a ** 3 - a) * m[i] + (b ** 3 - b) * m[i + 1]) * hi ** 2 / 6.0)


def linear_interp(xs: Vector, ys: Vector, x: float) -> float:
    i = 0
    while i < len(xs) - 2 and x > xs[i + 1]:
        i += 1
    t = (x - xs[i]) / (xs[i + 1] - xs[i])
    return ys[i] * (1 - t) + ys[i + 1] * t


def roughness(sample: Vector) -> float:
    """Sum of squared second differences: a proxy for how jagged a curve is."""
    return sum((sample[i + 1] - 2 * sample[i] + sample[i - 1]) ** 2
               for i in range(1, len(sample) - 1))


def main() -> None:
    import math

    xs = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    ys = [math.sin(x) for x in xs]
    spline = CubicSpline(xs, ys)

    # Interpolation property: the spline reproduces every knot exactly.
    max_knot_err = max(abs(spline(x) - y) for x, y in zip(xs, ys))
    print(f"max error at knots: {max_knot_err:.2e}  (should be ~0)")

    # Natural boundary: second derivative is zero at both ends.
    print(f"second derivatives m: {[round(v, 4) for v in spline.m]}")
    print(f"  m[0] = {spline.m[0]:.2e}, m[-1] = {spline.m[-1]:.2e} "
          f"(natural ends)")

    # Accuracy between knots, against the true sin it was sampled from.
    fine = [i * 0.1 for i in range(51)]
    spline_vals = [spline(x) for x in fine]
    lin_vals = [linear_interp(xs, ys, x) for x in fine]
    spline_max = max(abs(spline(x) - math.sin(x)) for x in fine)
    lin_max = max(abs(linear_interp(xs, ys, x) - math.sin(x)) for x in fine)
    print(f"\nmax |value - sin(x)| on a fine grid")
    print(f"  cubic spline: {spline_max:.5f}")
    print(f"  linear:       {lin_max:.5f}")
    print(f"  spline is closer to the true curve: {spline_max < lin_max}")

    # Smoothness: the spline is far less jagged than the linear interpolant.
    print(f"\nroughness (sum of squared 2nd differences on the fine grid)")
    print(f"  cubic spline: {roughness(spline_vals):.5f}")
    print(f"  linear:       {roughness(lin_vals):.5f}")
    print(f"  spline is smoother: "
          f"{roughness(spline_vals) < roughness(lin_vals)}")

    # A midpoint sample, cubic vs linear vs truth.
    x = 2.5
    print(f"\nat x = {x}: spline {spline(x):.5f}, "
          f"linear {linear_interp(xs, ys, x):.5f}, sin {math.sin(x):.5f}")


if __name__ == "__main__":
    main()
