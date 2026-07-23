"""Dinic's algorithm: max flow using level graphs and blocking flows.

Dinic speeds up Ford-Fulkerson by pushing many augmenting paths per round
instead of one. Each round begins with a BFS from the source that labels every
node with its distance in the residual graph — its level. Flow is then only ever
pushed along edges that step from one level to the next, u to v with
level[v] == level[u] + 1, so the search cannot wander sideways or backwards.

A single DFS finds a blocking flow in this level graph: it keeps sending flow
until no source-sink path made of level-advancing edges survives. Because every
such path strictly increases in level at each hop, no node is ever revisited on
one path, and dead ends are pruned with a per-node "next edge" pointer so the
whole blocking phase costs O(VE).

The magic is that the source-sink distance grows by at least one after every
blocking flow, so there are at most V rounds. That gives O(V^2 E) overall —
markedly better than Edmonds-Karp's O(VE^2) — and O(E*sqrt(V)) on unit-capacity
graphs, which is what makes it the engine behind Hopcroft-Karp matching.
"""

from collections import deque


class Dinic:
    def __init__(self, n: int) -> None:
        self.n = n
        # adj[u] holds indices into the flat edge list `edges`.
        self.adj: list[list[int]] = [[] for _ in range(n)]
        self.edges: list[list[int]] = []  # each: [to, capacity]

    def add_edge(self, u: int, v: int, cap: int) -> None:
        self.adj[u].append(len(self.edges))
        self.edges.append([v, cap])
        self.adj[v].append(len(self.edges))
        self.edges.append([u, 0])  # reverse edge starts empty

    def _bfs(self, s: int, t: int, level: list[int]) -> bool:
        for i in range(self.n):
            level[i] = -1
        level[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for eid in self.adj[u]:
                v, cap = self.edges[eid]
                if cap > 0 and level[v] == -1:
                    level[v] = level[u] + 1
                    queue.append(v)
        return level[t] != -1

    def _dfs(
        self, u: int, t: int, pushed: int, level: list[int], it: list[int]
    ) -> int:
        if u == t:
            return pushed
        # it[u] skips edges already known to be dead ends this phase.
        while it[u] < len(self.adj[u]):
            eid = self.adj[u][it[u]]
            v, cap = self.edges[eid]
            if cap > 0 and level[v] == level[u] + 1:
                got = self._dfs(v, t, min(pushed, cap), level, it)
                if got > 0:
                    self.edges[eid][1] -= got
                    self.edges[eid ^ 1][1] += got  # paired reverse edge
                    return got
            it[u] += 1
        return 0

    def max_flow(self, s: int, t: int) -> int:
        flow = 0
        level = [-1] * self.n
        while self._bfs(s, t, level):
            it = [0] * self.n
            while (pushed := self._dfs(s, t, float("inf"), level, it)) > 0:
                flow += pushed
        return flow

    def min_cut(self, s: int) -> set[int]:
        """Nodes reachable from s in the residual graph — the source side."""
        seen: set[int] = set()
        stack = [s]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            for eid in self.adj[u]:
                v, cap = self.edges[eid]
                if cap > 0 and v not in seen:
                    stack.append(v)
        return seen


def main() -> None:
    # Same classic network as many textbooks; nodes 0=S .. 5=T.
    # S -> 1 (16), S -> 2 (13), 1 -> 2 (10), 2 -> 1 (4), 1 -> 3 (12),
    # 3 -> 2 (9), 2 -> 4 (14), 4 -> 3 (7), 3 -> T (20), 4 -> T (4)
    dinic = Dinic(6)
    edges = [
        (0, 1, 16), (0, 2, 13), (1, 2, 10), (2, 1, 4), (1, 3, 12),
        (3, 2, 9), (2, 4, 14), (4, 3, 7), (3, 5, 20), (4, 5, 4),
    ]
    for u, v, c in edges:
        dinic.add_edge(u, v, c)

    flow = dinic.max_flow(0, 5)
    print(f"max flow 0 -> 5: {flow} (known answer 23)")
    assert flow == 23

    source_side = dinic.min_cut(0)
    cut = [
        (u, v)
        for (u, v, c) in edges
        if u in source_side and v not in source_side
    ]
    cut_value = sum(c for (u, v, c) in edges if u in source_side and v not in source_side)
    print(f"min cut edges: {cut}")
    print(f"min cut capacity: {cut_value}")
    assert cut_value == flow

    # Edge case: two parallel disjoint paths add up.
    para = Dinic(4)
    for u, v, c in [(0, 1, 5), (1, 3, 5), (0, 2, 7), (2, 3, 7)]:
        para.add_edge(u, v, c)
    print(f"parallel paths flow: {para.max_flow(0, 3)} (expect 12)")


if __name__ == "__main__":
    main()
