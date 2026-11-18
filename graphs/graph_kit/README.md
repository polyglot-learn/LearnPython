# graph_kit

A small `Graph` class (directed or undirected, weighted) with BFS, DFS, Dijkstra, topological sort, connected components, Kruskal MST and cycle detection.

```bash
python3 -m graphs.graph_kit     # eight examples plus a self-check
```

```python
from graphs.graph_kit import Graph, shortest_path

g = Graph.from_edges([("a", "b", 1), ("b", "c", 2), ("a", "c", 5)])
shortest_path(g, "a", "c")      # (3.0, ['a', 'b', 'c'])
```

- `graph.py` is the data structure; `algorithms.py` holds the algorithms.
- Dijkstra rejects negative weights; topological sort rejects cycles.
- Standalone versions live next to this folder, e.g. `../dijkstra.py`.
