"""Prim's algorithm: grow a minimum spanning tree outwards from one node.

Prim starts with a single node and repeatedly adds the cheapest edge that
leaves the tree built so far. The set of nodes in the tree is one side of a cut,
and the cheapest edge crossing any cut is always safe to add to some minimum
spanning tree — that cut property is what makes the greedy choice correct.

A min-heap of candidate edges does the bookkeeping. Push every edge out of a
newly added node; pop the cheapest; skip it if its far end is already in the
tree, since that edge no longer crosses the cut. This mirrors Dijkstra's
structure, with one difference worth pausing on: Dijkstra keys the heap on the
distance from the source, Prim on the weight of the single connecting edge.

Compared with Kruskal, Prim keeps one connected blob throughout and never needs
union-find, which suits dense graphs and adjacency lists; Kruskal sorts all
edges globally and suits sparse ones. On a disconnected graph Prim only ever
reaches the component it started in, whereas Kruskal returns a whole forest.

Complexity: O(E log E) time and O(E) space with a binary heap.
"""

import heapq

Graph = dict[str, list[tuple[str, float]]]
Edge = tuple[str, str, float]


def prim(graph: Graph, start: str) -> tuple[list[Edge], float]:
    """MST of the component containing start; returns its edges and total weight."""
    in_tree = {start}
    tree: list[Edge] = []
    total = 0.0
    heap: list[tuple[float, str, str]] = [
        (w, start, v) for v, w in graph.get(start, [])
    ]
    heapq.heapify(heap)

    while heap and len(in_tree) < len(graph):
        weight, source, target = heapq.heappop(heap)
        # Stale candidate: the far end joined the tree by a cheaper edge.
        if target in in_tree:
            continue
        in_tree.add(target)
        tree.append((source, target, weight))
        total += weight
        for neighbour, w in graph.get(target, []):
            if neighbour not in in_tree:
                heapq.heappush(heap, (w, target, neighbour))
    return tree, total


def main() -> None:
    #  the same graph Kruskal is usually shown on, as an adjacency list
    graph: Graph = {
        "A": [("B", 7), ("D", 5)],
        "B": [("A", 7), ("C", 8), ("D", 9), ("E", 7)],
        "C": [("B", 8), ("E", 5)],
        "D": [("A", 5), ("B", 9), ("E", 15), ("F", 6)],
        "E": [("B", 7), ("C", 5), ("D", 15), ("F", 8), ("G", 9)],
        "F": [("D", 6), ("E", 8), ("G", 11)],
        "G": [("E", 9), ("F", 11)],
    }

    tree, total = prim(graph, "A")
    for u, v, w in tree:
        print(f"{u} - {v}  weight {w:g}")
    print(f"total weight: {total:g}")
    print(f"edges: {len(tree)} for {len(graph)} nodes")

    # Starting elsewhere can pick a different edge order, but the total weight
    # of a minimum spanning tree is the same from any start.
    _, from_g = prim(graph, "G")
    print(f"total from G: {from_g:g}")

    # Prim stays inside one component, so a disconnected graph gives a partial
    # tree; Kruskal would have returned both components as a forest.
    split: Graph = {
        "A": [("B", 1)],
        "B": [("A", 1)],
        "C": [("D", 2)],
        "D": [("C", 2)],
    }
    print(f"disconnected, from A: {prim(split, 'A')}")

    # Edge cases: a lone node, and a duplicate edge that loses to the cheaper one.
    print(f"single node: {prim({'X': []}, 'X')}")
    twin: Graph = {"P": [("Q", 4), ("Q", 2)], "Q": [("P", 4), ("P", 2)]}
    print(f"parallel edges: {prim(twin, 'P')}")


if __name__ == "__main__":
    main()
