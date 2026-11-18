"""Graph algorithms that operate on a ``Graph``."""

import heapq
from collections import deque

from .graph import Graph, Node


def bfs_order(g: Graph, start: Node) -> list[Node]:
    seen, order, queue = {start}, [], deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in g.neighbors(node):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return order


def dfs_order(g: Graph, start: Node) -> list[Node]:
    seen, order, stack = set(), [], [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        stack.extend(reversed(list(g.neighbors(node))))  # visit in insertion order
    return order


def shortest_path(g: Graph, src: Node, dst: Node) -> tuple[float, list[Node]]:
    """Dijkstra. Returns (distance, path); (inf, []) if unreachable."""
    dist = {src: 0.0}
    prev: dict[Node, Node] = {}
    heap = [(0.0, 0, src)]
    tie = 1  # keeps heap comparisons off the nodes themselves
    while heap:
        d, _, node = heapq.heappop(heap)
        if d > dist.get(node, float("inf")):
            continue
        if node == dst:
            break
        for nxt, w in g.neighbors(node).items():
            if w < 0:
                raise ValueError("Dijkstra needs non-negative weights")
            nd = d + w
            if nd < dist.get(nxt, float("inf")):
                dist[nxt], prev[nxt] = nd, node
                heapq.heappush(heap, (nd, tie, nxt))
                tie += 1
    if dst not in dist:
        return float("inf"), []
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    return dist[dst], path[::-1]


def topological_sort(g: Graph) -> list[Node]:
    """Kahn's algorithm. Raises ValueError on a cycle."""
    if not g.directed:
        raise ValueError("topological sort needs a directed graph")
    indegree = {n: 0 for n in g.nodes}
    for _, v, _ in g.edges():
        indegree[v] += 1
    queue = deque(n for n, d in indegree.items() if d == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in g.neighbors(node):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    if len(order) != len(g):
        raise ValueError("graph has a cycle")
    return order


def connected_components(g: Graph) -> list[list[Node]]:
    """Components of an undirected graph, each in BFS order."""
    seen: set[Node] = set()
    out = []
    for node in g.nodes:
        if node not in seen:
            comp = bfs_order(g, node)
            seen.update(comp)
            out.append(comp)
    return out


def minimum_spanning_tree(g: Graph) -> tuple[float, list[tuple[Node, Node, float]]]:
    """Kruskal with union-find on an undirected graph."""
    parent = {n: n for n in g.nodes}

    def find(x: Node) -> Node:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total, chosen = 0.0, []
    for u, v, w in sorted(g.edges(), key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
            chosen.append((u, v, w))
    return total, chosen


def has_cycle(g: Graph) -> bool:
    if g.directed:
        try:
            topological_sort(g)
            return False
        except ValueError:
            return True
    # Undirected: a forest has exactly (nodes - components) edges.
    return len(list(g.edges())) > len(g) - len(connected_components(g))
