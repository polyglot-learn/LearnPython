"""Reporting intersecting segment pairs with a sweep line and event queue.

Testing every pair of n segments for intersection is O(n**2). A sweep line does
better by moving an imaginary vertical line left to right and only ever
considering segments that overlap in x at the same moment. The events are the
segment endpoints, sorted by x; entering an event's left endpoint adds a segment
to the active set, and passing its right endpoint removes it. Two segments can
only cross while both are active, so we never compare segments whose x-ranges are
disjoint.

The full Bentley-Ottmann algorithm goes further: it keeps the active segments
ordered by their y at the sweep line and checks only vertically adjacent pairs,
adding future crossing points as new events, reaching O((n + k) log n) for k
intersections. This file keeps the sweep and the event queue but, for clarity,
compares each entering segment against the whole active set rather than tracking
y-order — still a real pruning, and easy to see correct. It is cross-checked
against the all-pairs test.

Complexity: this simplified sweep is O(n log n + comparisons); worst case
O(n**2), but far fewer comparisons than all-pairs on typical inputs.
"""

Point = tuple[float, float]
Segment = tuple[Point, Point]


def _orient(a: Point, b: Point, c: Point) -> int:
    v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


def _on_segment(a: Point, b: Point, p: Point) -> bool:
    """Whether p, known collinear with a-b, lies within the segment box."""
    return (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))


def segments_intersect(s1: Segment, s2: Segment) -> bool:
    a, b = s1
    c, d = s2
    o1, o2 = _orient(a, b, c), _orient(a, b, d)
    o3, o4 = _orient(c, d, a), _orient(c, d, b)
    if o1 != o2 and o3 != o4:
        return True
    # Collinear touching / overlap cases.
    if o1 == 0 and _on_segment(a, b, c):
        return True
    if o2 == 0 and _on_segment(a, b, d):
        return True
    if o3 == 0 and _on_segment(c, d, a):
        return True
    if o4 == 0 and _on_segment(c, d, b):
        return True
    return False


def sweep_intersections(segments: list[Segment]) -> set[tuple[int, int]]:
    """Return the set of index pairs (i < j) whose segments intersect."""
    # Normalise each segment so the left endpoint comes first.
    norm = [seg if seg[0] <= seg[1] else (seg[1], seg[0]) for seg in segments]
    events: list[tuple[float, int, int]] = []
    for idx, (p, q) in enumerate(norm):
        events.append((p[0], 0, idx))  # 0 = left endpoint (enter)
        events.append((q[0], 1, idx))  # 1 = right endpoint (leave)
    events.sort()

    active: set[int] = set()
    found: set[tuple[int, int]] = set()
    for _, kind, idx in events:
        if kind == 0:
            for other in active:
                if segments_intersect(norm[idx], norm[other]):
                    found.add((min(idx, other), max(idx, other)))
            active.add(idx)
        else:
            active.discard(idx)
    return found


def brute_force(segments: list[Segment]) -> set[tuple[int, int]]:
    out: set[tuple[int, int]] = set()
    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            if segments_intersect(segments[i], segments[j]):
                out.add((i, j))
    return out


def main() -> None:
    segs: list[Segment] = [
        ((0.0, 0.0), (4.0, 4.0)),   # 0
        ((0.0, 4.0), (4.0, 0.0)),   # 1 crosses 0 at (2,2)
        ((5.0, 0.0), (5.0, 5.0)),   # 2 vertical, isolated
        ((1.0, 3.0), (6.0, 3.0)),   # 3 crosses 0, 1 and 2
    ]
    hits = sweep_intersections(segs)
    print(f"intersecting pairs (sweep): {sorted(hits)}")
    assert hits == brute_force(segs)

    import random
    random.seed(9)
    for _ in range(300):
        n = random.randint(0, 15)
        rnd: list[Segment] = []
        for _ in range(n):
            a = (random.randint(0, 8), random.randint(0, 8))
            b = (random.randint(0, 8), random.randint(0, 8))
            rnd.append((a, b))
        assert sweep_intersections(rnd) == brute_force(rnd)
    print("random cross-checks: sweep == all-pairs (300 runs)")

    print("\nedge cases:")
    print("  no segments:", sweep_intersections([]))
    print("  one segment:", sweep_intersections([((0.0, 0.0), (1.0, 1.0))]))
    touching: list[Segment] = [((0.0, 0.0), (2.0, 0.0)),
                               ((2.0, 0.0), (4.0, 0.0))]
    print("  endpoint touch:", sorted(sweep_intersections(touching)))


if __name__ == "__main__":
    main()
