"""Examples and self-check: python3 -m graphs.graph_kit"""

import sys

from . import (
    Graph,
    bfs_order,
    connected_components,
    dfs_order,
    has_cycle,
    minimum_spanning_tree,
    shortest_path,
    topological_sort,
)


def examples() -> None:
    roads = Graph.from_edges([
        ("A", "B", 4), ("A", "C", 2), ("B", "C", 1), ("B", "D", 5), ("C", "D", 8), ("D", "E", 3),
    ])
    print("1. BFS from A:", bfs_order(roads, "A"))
    print("2. DFS from A:", dfs_order(roads, "A"))
    print("3. shortest A->E:", shortest_path(roads, "A", "E"))
    total, edges = minimum_spanning_tree(roads)
    print("4. MST weight", total, "using", [(u, v) for u, v, _ in edges])
    islands = Graph.from_edges([(1, 2), (2, 3), (10, 11)]).add_node(99)
    print("5. components:", connected_components(islands))
    tasks = Graph.from_edges(
        [("wake", "dress"), ("dress", "shoes"), ("wake", "coffee"), ("coffee", "leave"),
         ("shoes", "leave")], directed=True)
    print("6. task order:", topological_sort(tasks))
    print("7. cycles:", has_cycle(roads), has_cycle(tasks), has_cycle(tasks.add_edge("leave", "wake")))
    print("8. unreachable:", shortest_path(Graph.from_edges([(1, 2)]).add_node(3), 1, 3))


def self_check() -> None:
    g = Graph.from_edges([("a", "b", 1), ("b", "c", 2), ("a", "c", 5)])
    assert shortest_path(g, "a", "c") == (3.0, ["a", "b", "c"])
    assert bfs_order(g, "a") == ["a", "b", "c"]
    assert minimum_spanning_tree(g)[0] == 3
    dag = Graph.from_edges([(1, 2), (1, 3), (2, 4), (3, 4)], directed=True)
    order = topological_sort(dag)
    assert all(order.index(u) < order.index(v) for u, v, _ in dag.edges())
    try:
        topological_sort(dag.add_edge(4, 1))
    except ValueError:
        pass
    else:
        raise AssertionError("cycle not detected")
    try:
        shortest_path(Graph.from_edges([(1, 2, -1)], directed=True), 1, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("negative weight not rejected")


def main() -> int:
    examples()
    self_check()
    print("self-check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
