"""Diameter of a point set via rotating calipers over its convex hull.

The diameter is the greatest distance between any two points. The farthest pair
always lies on the convex hull, so we first build the hull, then exploit a
monotonicity: as one hull edge rotates, the vertex farthest from it also moves
forward and never backward. Rotating calipers walks a second pointer around the
hull in lockstep, advancing it only while doing so increases the perpendicular
distance from the current edge, so together the two pointers make a single O(n)
loop around the hull.

Distance from the edge is measured by the cross product (twice the triangle
area), which avoids square roots during the search; we only take the actual
Euclidean distance when recording candidate antipodal pairs. The candidates are
exactly the vertex pairs where the calipers are parallel, and the largest of
those is the diameter.

Building the hull is O(n log n) and the calipers pass is O(n). This file
cross-checks against the brute-force all-pairs maximum.

Complexity: O(n log n) dominated by the hull sort.
"""

import math
import random

Point = tuple[float, float]


def _cross(o: Point, a: Point, b: Point) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def convex_hull(points: list[Point]) -> list[Point]:
    """Counter-clockwise hull, corners only, via monotone chain."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def build(seq: list[Point]) -> list[Point]:
        stack: list[Point] = []
        for p in seq:
            while len(stack) >= 2 and _cross(stack[-2], stack[-1], p) <= 0:
                stack.pop()
            stack.append(p)
        return stack

    lower = build(pts)
    upper = build(pts[::-1])
    return lower[:-1] + upper[:-1]


def _dist2(a: Point, b: Point) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def diameter(points: list[Point]) -> tuple[float, tuple[Point, Point]]:
    """Return (distance, (p, q)) for the farthest pair; needs >= 2 points."""
    if len(points) < 2:
        raise ValueError("need at least two points")
    hull = convex_hull(points)
    m = len(hull)
    if m == 1:  # all points identical
        return 0.0, (hull[0], hull[0])
    if m == 2:
        return math.sqrt(_dist2(hull[0], hull[1])), (hull[0], hull[1])

    best2 = 0.0
    best_pair = (hull[0], hull[1])
    j = 1
    for i in range(m):
        ni = (i + 1) % m
        # Advance j while the next vertex is farther from edge (hull[i], hull[ni]).
        while (abs(_cross(hull[i], hull[ni], hull[(j + 1) % m]))
               > abs(_cross(hull[i], hull[ni], hull[j]))):
            j = (j + 1) % m
        for v in (j, (j + 1) % m):
            d2 = _dist2(hull[i], hull[v])
            if d2 > best2:
                best2 = d2
                best_pair = (hull[i], hull[v])
    return math.sqrt(best2), best_pair


def brute_force(points: list[Point]) -> float:
    best = 0.0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            best = max(best, _dist2(points[i], points[j]))
    return math.sqrt(best)


def main() -> None:
    square: list[Point] = [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0),
                           (2.0, 2.0)]
    d, (p, q) = diameter(square)
    print(f"unit square + centre: diameter {d:.4f} between {p} and {q}")
    assert abs(d - brute_force(square)) < 1e-9

    random.seed(5)
    for _ in range(300):
        n = random.randint(2, 60)
        pts = [(random.uniform(0, 100), random.uniform(0, 100))
               for _ in range(n)]
        assert abs(diameter(pts)[0] - brute_force(pts)) < 1e-9
    print("random cross-checks: rotating calipers == brute force (300 runs)")

    print("\nedge cases:")
    print("  two points:", diameter([(0.0, 0.0), (3.0, 4.0)])[0])
    line: list[Point] = [(0.0, 0.0), (1.0, 1.0), (5.0, 5.0), (2.0, 2.0)]
    print("  collinear points:", round(diameter(line)[0], 4))


if __name__ == "__main__":
    main()
