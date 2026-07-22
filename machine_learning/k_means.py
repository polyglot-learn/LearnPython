"""k-means: alternate between assigning points and moving centroids.

Lloyd's algorithm repeats two steps. Assign every point to its nearest centroid,
then move each centroid to the mean of the points assigned to it. Both steps can
only lower the inertia — the total squared distance from points to their own
centroid — so the process is guaranteed to converge, and it does so quickly.

What it is not guaranteed to find is the best clustering. The result depends
entirely on where the centroids started, and a bad start can strand two centroids
inside one blob. k-means++ fixes most of that by seeding greedily: the first
centroid is a random point, and each later one is drawn with probability
proportional to its squared distance from the nearest centroid already chosen.
That gives an expected inertia within O(log k) of optimal before a single
iteration of Lloyd's has run.

We stop when the largest centroid movement falls below a tolerance rather than
after a fixed iteration count. Each iteration costs O(n * k * d).
"""

import math
import random


Point = list[float]


def squared_distance(a: Point, b: Point) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def kmeans_plus_plus(points: list[Point], k: int,
                     rng: random.Random) -> list[Point]:
    """Seed centroids far apart, weighted by squared distance."""
    centroids = [list(rng.choice(points))]
    while len(centroids) < k:
        weights = [min(squared_distance(p, c) for c in centroids) for p in points]
        total = sum(weights)
        if total == 0:
            # Fewer distinct points than k; duplicate one rather than fail.
            centroids.append(list(rng.choice(points)))
            continue
        target = rng.random() * total
        running = 0.0
        for point, w in zip(points, weights):
            running += w
            if running >= target:
                centroids.append(list(point))
                break
    return centroids


def assign(points: list[Point], centroids: list[Point]) -> list[int]:
    labels = []
    for p in points:
        best, best_d = 0, math.inf
        for i, c in enumerate(centroids):
            d = squared_distance(p, c)
            if d < best_d:
                best, best_d = i, d
        labels.append(best)
    return labels


def inertia(points: list[Point], centroids: list[Point],
            labels: list[int]) -> float:
    return sum(squared_distance(p, centroids[l]) for p, l in zip(points, labels))


def recentre(points: list[Point], labels: list[int], centroids: list[Point],
             k: int) -> list[Point]:
    d = len(points[0])
    sums = [[0.0] * d for _ in range(k)]
    counts = [0] * k
    for p, l in zip(points, labels):
        counts[l] += 1
        for j in range(d):
            sums[l][j] += p[j]
    # An empty cluster has no mean; leaving the old centroid in place is the
    # simplest safe choice and keeps the inertia monotone.
    return [[s / counts[i] for s in sums[i]] if counts[i] else list(centroids[i])
            for i in range(k)]


def k_means(points: list[Point], k: int, seed: int = 0, tol: float = 1e-6,
            max_iters: int = 100, verbose: bool = False
            ) -> tuple[list[Point], list[int], float]:
    if k <= 0 or not points:
        raise ValueError("need k > 0 and a non-empty dataset")
    rng = random.Random(seed)
    centroids = kmeans_plus_plus(points, k, rng)
    labels = assign(points, centroids)
    for it in range(1, max_iters + 1):
        new_centroids = recentre(points, labels, centroids, k)
        shift = max(math.sqrt(squared_distance(a, b))
                    for a, b in zip(centroids, new_centroids))
        centroids = new_centroids
        labels = assign(points, centroids)
        if verbose:
            print(f"  iteration {it:>2}: inertia "
                  f"{inertia(points, centroids, labels):>10.4f}  "
                  f"max shift {shift:.6f}")
        if shift < tol:
            break
    return centroids, labels, inertia(points, centroids, labels)


def main() -> None:
    rng = random.Random(3)
    centres = [(0.0, 0.0), (8.0, 1.0), (4.0, 7.0)]
    points: list[Point] = []
    for cx, cy in centres:
        for _ in range(60):
            points.append([rng.gauss(cx, 0.8), rng.gauss(cy, 0.8)])

    print("three blobs, k = 3, k-means++ seeding")
    centroids, labels, final = k_means(points, 3, seed=42, verbose=True)
    print(f"final inertia: {final:.4f}")
    for i, c in enumerate(sorted(centroids, key=lambda c: (c[0], c[1]))):
        print(f"  centroid {i}: ({c[0]:.3f}, {c[1]:.3f})")
    print("  cluster sizes: " +
          ", ".join(str(labels.count(i)) for i in range(3)))
    print("  true centres:  " +
          ", ".join(f"({x}, {y})" for x, y in centres))

    # More clusters always lowers inertia; the elbow is where it stops helping.
    print("\ninertia versus k")
    for k in range(1, 7):
        _, _, score = k_means(points, k, seed=42)
        print(f"  k = {k}: {score:>10.4f}")

    # Plain random seeding can strand two centroids in one blob; with k-means++
    # every seed here finds the same optimum, which is the whole point of it.
    print("\nseed sensitivity at k = 3")
    for seed in (0, 1, 2, 7, 99):
        _, _, score = k_means(points, 3, seed=seed)
        print(f"  seed {seed:>2}: inertia {score:.4f}")

    print("\nedge cases")
    single = [[1.0, 1.0]]
    c, _, s = k_means(single, 1)
    print(f"  one point, k = 1: centroid {c[0]}, inertia {s}")
    dupes = [[2.0, 2.0]] * 5
    c, _, s = k_means(dupes, 3, seed=1)
    print(f"  five identical points, k = 3: inertia {s}, "
          f"distinct centroids {len({tuple(x) for x in c})}")
    c, _, s = k_means(points, len(points), seed=1)
    print(f"  k = n ({len(points)}): inertia {s:.6f} (each point its own cluster)")
    try:
        k_means([], 2)
    except ValueError as exc:
        print(f"  empty dataset: ValueError({exc})")


if __name__ == "__main__":
    main()
