"""Bellman-Ford: shortest paths that tolerate negative edge weights.

Dijkstra is greedy and needs non-negative weights. Bellman-Ford gives that up
and brute-forces instead: relax every edge in the graph, then do it again, V-1
times in total.

The bound comes from a counting argument. A shortest path in a graph with no
negative cycle is simple, so it uses at most V-1 edges. After one full pass
every correct one-edge prefix is settled, after two passes every two-edge
prefix, and so on — so V-1 passes settle every shortest path there is.

That also hands you a free negative-cycle detector. Run one extra pass: if any
edge still improves, some path keeps getting cheaper the more you go round, so
a reachable negative cycle exists and "shortest path" is meaningless there.

Complexity: O(V * E) time and O(V) space — far slower than Dijkstra, which is
why you only reach for it when weights can go negative.
"""

Edge = tuple[str, str, float]


def bellman_ford(
    nodes: list[str], edges: list[Edge], start: str
) -> tuple[dict[str, float], dict[str, str | None]] | None:
    """Distances and parents from start, or None if a negative cycle is reachable."""
    dist: dict[str, float] = {n: float("inf") for n in nodes}
    parent: dict[str, str | None] = {n: None for n in nodes}
    dist[start] = 0.0

    for _ in range(len(nodes) - 1):
        changed = False
        for u, v, w in edges:
            # inf + w would relax edges out of unreachable nodes.
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                changed = True
        if not changed:
            break  # settled early; further passes cannot change anything

    for u, v, w in edges:
        if dist[u] != float("inf") and dist[u] + w < dist[v]:
            return None
    return dist, parent


def find_negative_cycle(nodes: list[str], edges: list[Edge], start: str) -> list[str] | None:
    """Return the nodes of one reachable negative cycle, or None if there is none."""
    dist: dict[str, float] = {n: float("inf") for n in nodes}
    parent: dict[str, str | None] = {n: None for n in nodes}
    dist[start] = 0.0
    victim: str | None = None

    for _ in range(len(nodes)):
        victim = None
        for u, v, w in edges:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                victim = v
    if victim is None:
        return None

    # The victim may only be downstream of the cycle, so walk back V steps to
    # land on it for certain, then walk the parent ring once.
    node = victim
    for _ in range(len(nodes)):
        node = parent[node]  # type: ignore[assignment]
    cycle = [node]
    walker = parent[node]
    while walker != node:
        cycle.append(walker)  # type: ignore[arg-type]
        walker = parent[walker]  # type: ignore[index]
    cycle.append(node)
    cycle.reverse()
    return cycle


def path_to(parent: dict[str, str | None], goal: str) -> list[str]:
    path: list[str] = []
    node: str | None = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def main() -> None:
    nodes = ["S", "A", "B", "C", "D", "X"]
    edges: list[Edge] = [
        ("S", "A", 4),
        ("S", "B", 5),
        ("A", "C", 3),
        ("B", "A", -3),  # negative, but no cycle: Dijkstra would misreport A
        ("B", "D", 4),
        ("C", "D", -2),
    ]

    result = bellman_ford(nodes, edges, "S")
    assert result is not None
    dist, parent = result
    for node in nodes:
        print(f"S -> {node}: {dist[node]:g}")
    print(f"path S -> D: {path_to(parent, 'D')}")

    # X is listed but has no incoming edge, so it stays at infinity.
    print(f"unreachable X: {dist['X']}")

    # Add a cycle A -> C -> A with total weight 3 + (-5) = -2.
    cyclic = edges + [("C", "A", -5)]
    print(f"with a negative cycle: {bellman_ford(nodes, cyclic, 'S')}")
    print(f"cycle found: {find_negative_cycle(nodes, cyclic, 'S')}")
    print(f"cycle on the clean graph: {find_negative_cycle(nodes, edges, 'S')}")


if __name__ == "__main__":
    main()
