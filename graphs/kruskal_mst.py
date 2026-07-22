"""Kruskal's algorithm: build a minimum spanning tree from the cheapest edges up.

A spanning tree connects every node using V-1 edges and no cycles; the minimum
one has the smallest total weight. Kruskal sorts all edges by weight and walks
the list, keeping an edge only when its two endpoints are not already
connected. Adding an edge inside an existing component would close a cycle, and
a cycle can always be broken at its heaviest edge without disconnecting
anything.

Everything then rests on answering "are these two nodes already connected?"
quickly, which is exactly what a disjoint set (union-find) does in near-constant
time. The union call doubles as the test: it returns False when both endpoints
already share a root.

Kruskal grows a forest of unconnected fragments that merge at the end, so on a
disconnected graph it naturally produces a minimum spanning forest — check the
edge count to tell the two apart.

Complexity: O(E log E) time, dominated by the sort; O(V) space.
"""


class DisjointSet:
    """Union-find with path compression and union by rank."""

    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False  # already connected: this edge would make a cycle
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


Edge = tuple[int, int, float]


def kruskal(n: int, edges: list[Edge]) -> tuple[list[Edge], float]:
    """Minimum spanning tree (or forest) of n nodes; returns its edges and weight."""
    dsu = DisjointSet(n)
    tree: list[Edge] = []
    total = 0.0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if dsu.union(u, v):
            tree.append((u, v, w))
            total += w
            if len(tree) == n - 1:
                break  # a tree on n nodes cannot take any more edges
    return tree, total


def is_spanning(n: int, tree: list[Edge]) -> bool:
    return len(tree) == n - 1


def main() -> None:
    names = ["A", "B", "C", "D", "E", "F", "G"]
    edges: list[Edge] = [
        (0, 1, 7),
        (0, 3, 5),
        (1, 2, 8),
        (1, 3, 9),
        (1, 4, 7),
        (2, 4, 5),
        (3, 4, 15),
        (3, 5, 6),
        (4, 5, 8),
        (4, 6, 9),
        (5, 6, 11),
    ]

    tree, total = kruskal(len(names), edges)
    for u, v, w in tree:
        print(f"{names[u]} - {names[v]}  weight {w:g}")
    print(f"total weight: {total:g}")
    print(f"spans all nodes: {is_spanning(len(names), tree)}")

    # A disconnected graph yields a forest, not a tree: two components here,
    # so only n - 2 edges come back.
    forest, weight = kruskal(4, [(0, 1, 1), (2, 3, 2)])
    print(f"forest: {forest}, weight {weight:g}, spanning {is_spanning(4, forest)}")

    # Parallel edges and self-loops are harmless: the loop and the dearer
    # duplicate both fail the union test.
    messy, w2 = kruskal(3, [(0, 0, 1), (0, 1, 4), (0, 1, 2), (1, 2, 3)])
    print(f"messy input: {messy}, weight {w2:g}")

    # Edge cases: one node needs no edges, and zero nodes is not an error.
    print(f"single node: {kruskal(1, [])}")
    print(f"no nodes:    {kruskal(0, [])}")


if __name__ == "__main__":
    main()
