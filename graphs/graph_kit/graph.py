"""A small weighted graph (directed or undirected) stored as adjacency dicts."""

from collections.abc import Hashable, Iterator
from typing import Self

Node = Hashable


class Graph:
    def __init__(self, directed: bool = False) -> None:
        self.directed = directed
        self._adj: dict[Node, dict[Node, float]] = {}

    def add_node(self, node: Node) -> Self:
        self._adj.setdefault(node, {})
        return self

    def add_edge(self, u: Node, v: Node, weight: float = 1.0) -> Self:
        self.add_node(u)
        self.add_node(v)
        self._adj[u][v] = weight
        if not self.directed:
            self._adj[v][u] = weight
        return self

    @classmethod
    def from_edges(cls, edges: list[tuple], directed: bool = False) -> "Graph":
        """Build from ``(u, v)`` or ``(u, v, weight)`` tuples."""
        g = cls(directed)
        for edge in edges:
            g.add_edge(*edge)
        return g

    @property
    def nodes(self) -> list[Node]:
        return list(self._adj)

    def neighbors(self, node: Node) -> dict[Node, float]:
        return self._adj[node]

    def edges(self) -> Iterator[tuple[Node, Node, float]]:
        seen: set[frozenset] = set()
        for u, nbrs in self._adj.items():
            for v, w in nbrs.items():
                if not self.directed:
                    pair = frozenset((u, v))
                    if pair in seen:
                        continue
                    seen.add(pair)
                yield u, v, w

    def __contains__(self, node: Node) -> bool:
        return node in self._adj

    def __len__(self) -> int:
        return len(self._adj)
