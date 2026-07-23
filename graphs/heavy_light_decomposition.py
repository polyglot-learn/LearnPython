"""Heavy-light decomposition: turn tree paths into a few contiguous ranges.

Any root-to-node path in a tree crosses at most O(log n) distinct "chains" if we
build the chains greedily. At each node the child leading the largest subtree is
the heavy child; the edge to it is a heavy edge, and maximal runs of heavy edges
form chains. Because a light edge at least halves the remaining subtree size, any
path up the tree can enter at most O(log n) chains before reaching the root.

We flatten each chain into a contiguous block of positions, so a value indexed by
node lands in one array. A segment tree (here a simple Fenwick/BIT for sums) over
that array then answers a range query in O(log n). A path query between u and v
walks up the two chains alternately, summing one chain segment at a time, until
both sit on the same chain. Total cost per path query is O(log^2 n): O(log n)
chain hops, each a O(log n) range query.
"""


class FenwickTree:
    def __init__(self, n: int) -> None:
        self.tree = [0] * (n + 1)

    def update(self, i: int, delta: int) -> None:
        i += 1
        while i < len(self.tree):
            self.tree[i] += delta
            i += i & (-i)

    def prefix(self, i: int) -> int:
        i += 1
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & (-i)
        return total

    def range_sum(self, lo: int, hi: int) -> int:
        return self.prefix(hi) - (self.prefix(lo - 1) if lo > 0 else 0)


class HeavyLight:
    def __init__(self, n: int, tree: list[list[int]], root: int = 0) -> None:
        self.n = n
        self.tree = tree
        self.parent = [-1] * n
        self.depth = [0] * n
        self.size = [1] * n
        self.heavy = [-1] * n     # heavy child of each node
        self.head = [0] * n       # top of the chain a node belongs to
        self.pos = [0] * n        # flattened index of a node
        self._dfs_sizes(root)
        self._decompose(root, root)
        self.bit = FenwickTree(n)

    def _dfs_sizes(self, root: int) -> None:
        # Iterative post-order to compute subtree sizes and the heavy child.
        order: list[int] = []
        stack = [(root, -1)]
        while stack:
            node, par = stack.pop()
            self.parent[node] = par
            order.append(node)
            for nxt in self.tree[node]:
                if nxt != par:
                    self.depth[nxt] = self.depth[node] + 1
                    stack.append((nxt, node))
        for node in reversed(order):
            best = 0
            for nxt in self.tree[node]:
                if nxt == self.parent[node]:
                    continue
                self.size[node] += self.size[nxt]
                if self.size[nxt] > best:
                    best = self.size[nxt]
                    self.heavy[node] = nxt

    def _decompose(self, root: int, head: int) -> None:
        # Iterative walk: follow heavy edges to keep chain positions contiguous.
        counter = 0
        stack = [(root, head)]
        while stack:
            node, h = stack.pop()
            # Walk down the heavy chain from `node`, assigning positions.
            while node != -1:
                self.head[node] = h
                self.pos[node] = counter
                counter += 1
                # Light children start new chains; queue them.
                for nxt in self.tree[node]:
                    if nxt != self.parent[node] and nxt != self.heavy[node]:
                        stack.append((nxt, nxt))
                node = self.heavy[node]

    def set_value(self, node: int, value: int) -> None:
        old = self.bit.range_sum(self.pos[node], self.pos[node])
        self.bit.update(self.pos[node], value - old)

    def path_sum(self, u: int, v: int) -> int:
        total = 0
        while self.head[u] != self.head[v]:
            # Always climb from the deeper chain head.
            if self.depth[self.head[u]] < self.depth[self.head[v]]:
                u, v = v, u
            total += self.bit.range_sum(self.pos[self.head[u]], self.pos[u])
            u = self.parent[self.head[u]]
        lo, hi = sorted((self.pos[u], self.pos[v]))
        total += self.bit.range_sum(lo, hi)
        return total


def _naive_path_sum(tree: list[list[int]], values: list[int], u: int,
                    v: int) -> int:
    """Walk the actual tree path with a BFS parent chain and sum node values."""
    from collections import deque

    n = len(tree)
    parent = [-1] * n
    seen = [False] * n
    seen[u] = True
    q = deque([u])
    while q:
        node = q.popleft()
        for nxt in tree[node]:
            if not seen[nxt]:
                seen[nxt] = True
                parent[nxt] = node
                q.append(nxt)
    path = []
    cur = v
    while cur != u:
        path.append(cur)
        cur = parent[cur]
    path.append(u)
    return sum(values[node] for node in path)


def main() -> None:
    #        0
    #      / | \
    #     1  2  3
    #    / \     \
    #   4   5     6
    n = 7
    tree: list[list[int]] = [[] for _ in range(n)]
    for a, b in [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (3, 6)]:
        tree[a].append(b)
        tree[b].append(a)

    values = [10, 20, 30, 40, 50, 60, 70]
    hld = HeavyLight(n, tree, root=0)
    for node, val in enumerate(values):
        hld.set_value(node, val)

    for u, v in [(4, 6), (5, 2), (4, 5), (0, 6), (3, 3)]:
        got = hld.path_sum(u, v)
        want = _naive_path_sum(tree, values, u, v)
        print(f"path {u} - {v}: sum {got} (naive {want})")
        assert got == want, "HLD path sum must match naive walk"

    # Edge case: updating a value is reflected in later queries.
    hld.set_value(4, 100)
    values[4] = 100
    got = hld.path_sum(4, 6)
    want = _naive_path_sum(tree, values, 4, 6)
    print(f"after update, path 4 - 6: {got} (naive {want})")
    assert got == want

    print("all cross-checks passed")


if __name__ == "__main__":
    main()
