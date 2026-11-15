"""graph_kit: a ``Graph`` class plus BFS, DFS, Dijkstra, topological sort, MST.

    >>> from graphs.graph_kit import Graph, shortest_path
    >>> g = Graph.from_edges([("a", "b", 1), ("b", "c", 2), ("a", "c", 5)])
    >>> shortest_path(g, "a", "c")
    (3.0, ['a', 'b', 'c'])
"""

from .algorithms import (
    bfs_order,
    connected_components,
    dfs_order,
    has_cycle,
    minimum_spanning_tree,
    shortest_path,
    topological_sort,
)
from .graph import Graph

__all__ = [
    "Graph",
    "bfs_order",
    "dfs_order",
    "shortest_path",
    "topological_sort",
    "connected_components",
    "minimum_spanning_tree",
    "has_cycle",
]
