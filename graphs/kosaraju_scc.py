"""Kosaraju's algorithm: strongly connected components in two DFS passes.

Like Tarjan, this finds maximal groups where every vertex reaches every other,
but it trades one clever pass for two simple ones. First DFS the graph and push
each node onto a stack when it finishes; this orders nodes by decreasing finish
time. Then reverse every edge and DFS again, popping nodes off that stack: each
tree grown in the transpose is exactly one SCC.

Why it works: finishing late in the first pass means a node sits "upstream" in
the condensation DAG. Reversing the edges flips that DAG, so starting from the
latest-finishing node in the transpose can only reach its own component — the
downstream components it used to point to now point away from it.

Compared with Tarjan, Kosaraju is easier to reason about but walks the graph
twice and needs the transpose, so it does roughly double the work while staying
O(V + E). Tarjan is the one-pass, constant-factor-cheaper choice; Kosaraju wins
on clarity and when you already have the reverse graph handy.
"""

Graph = dict[str, list[str]]


def transpose(graph: Graph) -> Graph:
    rev: Graph = {node: [] for node in graph}
    for node, neighbours in graph.items():
        for nxt in neighbours:
            rev.setdefault(nxt, []).append(node)
            rev.setdefault(node, rev.get(node, []))
    return rev


def kosaraju_scc(graph: Graph) -> list[list[str]]:
    """Return the SCCs; each inner list is one component."""
    visited: set[str] = set()
    order: list[str] = []

    def dfs_finish(start: str) -> None:
        # Iterative post-order so deep graphs do not blow the recursion limit.
        stack: list[tuple[str, bool]] = [(start, False)]
        while stack:
            node, processed = stack.pop()
            if processed:
                order.append(node)
                continue
            if node in visited:
                continue
            visited.add(node)
            stack.append((node, True))
            for nxt in graph.get(node, []):
                if nxt not in visited:
                    stack.append((nxt, False))

    for node in graph:
        if node not in visited:
            dfs_finish(node)

    rev = transpose(graph)
    visited.clear()
    sccs: list[list[str]] = []

    def collect(start: str, comp: list[str]) -> None:
        stack = [start]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            comp.append(node)
            for nxt in rev.get(node, []):
                if nxt not in visited:
                    stack.append(nxt)

    for node in reversed(order):
        if node not in visited:
            comp: list[str] = []
            collect(node, comp)
            sccs.append(comp)
    return sccs


def main() -> None:
    #  A -> B -> C -> A   and   E <-> F,   D feeds into both
    graph: Graph = {
        "A": ["B"],
        "B": ["C"],
        "C": ["A"],
        "D": ["C", "E"],
        "E": ["F"],
        "F": ["E"],
        "G": [],
    }

    sccs = kosaraju_scc(graph)
    for comp in sccs:
        print(f"SCC: {sorted(comp)}")

    # Cross-check against a brute-force mutual-reachability definition.
    def reaches(g: Graph, s: str, t: str) -> bool:
        seen, stack = {s}, [s]
        while stack:
            n = stack.pop()
            if n == t:
                return True
            for m in g.get(n, []):
                if m not in seen:
                    seen.add(m)
                    stack.append(m)
        return s == t

    comp_of = {n: i for i, c in enumerate(sccs) for n in c}
    for u in graph:
        for v in graph:
            mutual = reaches(graph, u, v) and reaches(graph, v, u)
            assert mutual == (comp_of[u] == comp_of[v]), (u, v)
    print("brute-force mutual-reachability check passed")

    print(f"SCC count: {len(sccs)}")


if __name__ == "__main__":
    main()
