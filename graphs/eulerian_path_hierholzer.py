"""Hierholzer's algorithm: build an Eulerian path or circuit in O(V + E).

An Eulerian trail walks every edge exactly once; if it also ends where it began
it is an Eulerian circuit. Whether one exists is settled purely by degrees. For
an undirected connected graph: a circuit exists iff every vertex has even
degree, and an open trail exists iff exactly two vertices have odd degree (those
two are the endpoints). Any other count means no such walk.

Hierholzer's method assumes those conditions hold and stitches the trail
together. Start at a valid vertex and follow unused edges, deleting each as you
cross it, until you return to a stuck point — this closes a sub-tour. Whenever
the current vertex still has unused edges, dive into a new sub-tour from there
before recording the vertex; done iteratively with an explicit stack, vertices
pop into the final route in the correct order once they run dry.

Because every edge is consumed exactly once and each is touched a constant
number of times, the whole construction is O(V + E). This version handles the
undirected case and checks the degree and connectivity conditions up front,
returning None when no Eulerian trail can exist.
"""

from collections import defaultdict

Graph = dict[str, list[str]]


def eulerian_path(graph: Graph) -> list[str] | None:
    """Return an Eulerian trail as a vertex sequence, or None if impossible."""
    # Adjacency stores (neighbour, edge_id); both endpoints share an id so an
    # undirected edge is consumed exactly once regardless of which end uses it.
    adj: dict[str, list[tuple[str, int]]] = defaultdict(list)
    degree: dict[str, int] = defaultdict(int)
    edge_count = 0
    for u in graph:
        for v in graph[u]:
            if u < v:  # add each undirected edge once, from the smaller end
                eid = edge_count
                adj[u].append((v, eid))
                adj[v].append((u, eid))
                degree[u] += 1
                degree[v] += 1
                edge_count += 1

    if edge_count == 0:
        return None

    odd = [v for v in adj if degree[v] % 2 == 1]
    if len(odd) not in (0, 2):
        return None

    # All edges must lie in one connected component, else no single trail.
    start = odd[0] if odd else next(iter(adj))
    seen: set[str] = set()
    stack = [start]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        stack.extend(w for w, _ in adj[u])
    if any(degree[v] > 0 and v not in seen for v in adj):
        return None

    # Hierholzer: per-vertex pointer skips spent edges; a used-set marks each
    # edge id once so parallel edges are each crossed exactly one time.
    ptr: dict[str, int] = defaultdict(int)
    used: set[int] = set()
    circuit: list[str] = []
    walk = [start]
    while walk:
        u = walk[-1]
        while ptr[u] < len(adj[u]):
            v, eid = adj[u][ptr[u]]
            ptr[u] += 1
            if eid not in used:
                used.add(eid)
                walk.append(v)
                break
        else:
            circuit.append(walk.pop())
    circuit.reverse()

    if len(circuit) != edge_count + 1:
        return None  # graph was disconnected in edges after all
    return circuit


def main() -> None:
    #  A - B - C - A   (triangle, an Eulerian circuit)
    triangle: Graph = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B"],
    }
    circuit = eulerian_path(triangle)
    print(f"triangle circuit: {circuit}")
    assert circuit is not None and circuit[0] == circuit[-1]
    assert len(circuit) == 4  # 3 edges + return to start

    #  Open trail: vertices 2 and 3 have odd degree, so the walk runs 2 ... 3.
    path_graph: Graph = {
        "0": ["1", "2"],
        "1": ["0", "2"],
        "2": ["0", "1", "3"],
        "3": ["2"],
    }
    trail = eulerian_path(path_graph)
    print(f"open trail: {trail}")
    assert trail is not None and {trail[0], trail[-1]} == {"2", "3"}

    # Verify a returned trail actually uses every edge exactly once.
    def uses_all_edges(graph: Graph, seq: list[str]) -> bool:
        remaining: dict[tuple[str, str], int] = defaultdict(int)
        for u in graph:
            for v in graph[u]:
                if u < v:
                    remaining[(u, v)] += 1
        for a, b in zip(seq, seq[1:]):
            key = (min(a, b), max(a, b))
            remaining[key] -= 1
        return all(c == 0 for c in remaining.values())

    assert uses_all_edges(path_graph, trail)
    print("edge-coverage check passed")

    # Edge case: four odd-degree vertices -> no Eulerian trail.
    k4: Graph = {
        "A": ["B", "C", "D"],
        "B": ["A", "C", "D"],
        "C": ["A", "B", "D"],
        "D": ["A", "B", "C"],
    }
    print(f"K4 (all odd degree): {eulerian_path(k4)} (expect None)")

    # Edge case: disconnected edges -> None even with good degrees.
    split: Graph = {
        "A": ["B"], "B": ["A"],
        "X": ["Y"], "Y": ["X"],
    }
    print(f"disconnected: {eulerian_path(split)} (expect None)")


if __name__ == "__main__":
    main()
