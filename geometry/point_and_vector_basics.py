"""Points and vectors in 2-D: distance, dot product, cross product.

A point and a vector are the same pair of numbers used differently: a point is
a place, a vector is a displacement. Subtracting two points gives the vector
between them, which is why almost every geometry routine starts with b - a.

The dot product measures alignment: it is positive when two vectors point the
same way, zero when they are perpendicular, negative when opposed. The 2-D
cross product is a single scalar, the signed area of the parallelogram they
span, and its sign is the workhorse of computational geometry: cross(b - a,
c - a) is positive when a, b, c turn counter-clockwise, negative when they turn
clockwise, and exactly zero when they are collinear.

Comparing squared distances instead of distances avoids a square root. Squaring
is monotonic on non-negative numbers, so the ordering is identical, and with
integer inputs the comparison stays exact instead of drifting into float error.
All operations here are O(1).
"""

from math import atan2

Point = tuple[float, float]


def add(a: Point, b: Point) -> Point:
    return (a[0] + b[0], a[1] + b[1])


def sub(a: Point, b: Point) -> Point:
    return (a[0] - b[0], a[1] - b[1])


def scale(a: Point, k: float) -> Point:
    return (a[0] * k, a[1] * k)


def dot(a: Point, b: Point) -> float:
    return a[0] * b[0] + a[1] * b[1]


def cross(a: Point, b: Point) -> float:
    """Signed area of the parallelogram spanned by a and b (the z component)."""
    return a[0] * b[1] - a[1] * b[0]


def dist_sq(a: Point, b: Point) -> float:
    d = sub(a, b)
    return dot(d, d)


def dist(a: Point, b: Point) -> float:
    return dist_sq(a, b) ** 0.5


def orientation(a: Point, b: Point, c: Point) -> int:
    """+1 counter-clockwise, -1 clockwise, 0 collinear."""
    v = cross(sub(b, a), sub(c, a))
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


def nearest_point(target: Point, candidates: list[Point]) -> Point | None:
    """No sqrt: the closest by squared distance is the closest, full stop."""
    if not candidates:
        return None
    return min(candidates, key=lambda p: dist_sq(target, p))


def angle_between(a: Point, b: Point) -> float:
    """Radians in [0, pi]; uses atan2 of cross over dot for numeric stability."""
    return abs(atan2(cross(a, b), dot(a, b)))


def main() -> None:
    a: Point = (0.0, 0.0)
    b: Point = (4.0, 0.0)
    c: Point = (4.0, 3.0)

    print(f"b - a          = {sub(b, a)}")
    print(f"dist(a, c)     = {dist(a, c)}")
    print(f"dist_sq(a, c)  = {dist_sq(a, c)}  (no sqrt taken)")
    print(f"dot(b, c)      = {dot(b, c)}")
    print(f"cross(b, c)    = {cross(b, c)}")

    print(f"orientation ccw:       {orientation(a, b, c)}")
    print(f"orientation cw:        {orientation(a, c, b)}")
    print(f"orientation collinear: {orientation(a, b, (8.0, 0.0))}")

    # Perpendicular vectors have zero dot product; parallel ones zero cross.
    print(f"dot((1,0),(0,1))   = {dot((1.0, 0.0), (0.0, 1.0))}")
    print(f"cross((2,4),(1,2)) = {cross((2.0, 4.0), (1.0, 2.0))}")

    pts: list[Point] = [(10.0, 10.0), (1.0, 1.0), (-3.0, 0.0)]
    print(f"nearest to origin: {nearest_point((0.0, 0.0), pts)}")
    print(f"nearest of empty:  {nearest_point((0.0, 0.0), [])}")

    print(f"angle (1,0)-(0,1): {angle_between((1.0, 0.0), (0.0, 1.0)):.4f} rad")
    print(f"angle (1,0)-(1,0): {angle_between((1.0, 0.0), (1.0, 0.0)):.4f} rad")

    # Degenerate: a zero-length vector is neither left nor right of anything.
    print(f"orientation with duplicate point: {orientation(a, a, c)}")


if __name__ == "__main__":
    main()
