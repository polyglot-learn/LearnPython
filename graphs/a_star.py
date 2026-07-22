"""A* search: Dijkstra plus a hint about which direction the goal lies in.

Dijkstra expands nodes in order of g(n), the confirmed cost from the start, so
it spreads out evenly in all directions and wastes work exploring away from the
goal. A* orders the heap by f(n) = g(n) + h(n), where h(n) is an estimate of the
cost still to come. Nodes that look closer to the goal get popped first, so the
search leans towards it.

The estimate has to be admissible: h must never overestimate the true remaining
cost. If it does, A* can pop the goal while a cheaper route is still queued and
return a suboptimal path. On a grid with four-way movement and unit steps,
Manhattan distance is admissible, because you must make at least that many
moves no matter how you route. It is also consistent, which is the stronger
condition that lets you finalise each node on its first pop.

Setting h = 0 makes f = g, and A* degenerates into exactly Dijkstra. So A* is
not a different algorithm so much as Dijkstra with prior knowledge, and h
controls how much of the map you can skip.

Complexity: worst case the same as Dijkstra, O(E log V); in practice far fewer
nodes are expanded the better h is.
"""

import heapq

Cell = tuple[int, int]


def manhattan(a: Cell, b: Cell) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def zero(a: Cell, b: Cell) -> int:
    """The null heuristic, which turns A* back into Dijkstra."""
    return 0


def neighbours(grid: list[str], cell: Cell) -> list[Cell]:
    rows, cols = len(grid), len(grid[0])
    r, c = cell
    out = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#":
            out.append((nr, nc))
    return out


def a_star(
    grid: list[str], start: Cell, goal: Cell, heuristic=manhattan
) -> tuple[list[Cell] | None, int]:
    """Cheapest path from start to goal, plus how many nodes were expanded."""
    g_score: dict[Cell, int] = {start: 0}
    parent: dict[Cell, Cell | None] = {start: None}
    done: set[Cell] = set()
    expanded = 0
    heap: list[tuple[int, int, Cell]] = [(heuristic(start, goal), 0, start)]

    while heap:
        _, g, cell = heapq.heappop(heap)
        if cell in done:
            continue  # stale entry left over from an earlier, worse g
        done.add(cell)
        expanded += 1
        if cell == goal:
            return rebuild(parent, goal), expanded
        for nxt in neighbours(grid, cell):
            candidate = g + 1  # every step on this grid costs one
            if candidate < g_score.get(nxt, 1 << 30):
                g_score[nxt] = candidate
                parent[nxt] = cell
                heapq.heappush(heap, (candidate + heuristic(nxt, goal), candidate, nxt))
    return None, expanded


def rebuild(parent: dict[Cell, Cell | None], goal: Cell) -> list[Cell]:
    path: list[Cell] = []
    node: Cell | None = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def render(grid: list[str], path: list[Cell]) -> str:
    marked = [list(row) for row in grid]
    for r, c in path:
        marked[r][c] = "*"
    marked[path[0][0]][path[0][1]] = "S"
    marked[path[-1][0]][path[-1][1]] = "G"
    return "\n".join("".join(row) for row in marked)


def main() -> None:
    grid = [
        "..........",
        ".####.###.",
        ".#....#...",
        ".#.##.#.#.",
        "...#....#.",
        ".###.####.",
        ".....#....",
    ]
    start, goal = (0, 0), (6, 9)

    path, expanded = a_star(grid, start, goal)
    assert path is not None
    print(render(grid, path))
    print(f"path length: {len(path) - 1} steps, {expanded} cells expanded")

    # Same grid, h = 0: identical cost, but many more cells looked at.
    dij_path, dij_expanded = a_star(grid, start, goal, zero)
    assert dij_path is not None
    print(f"with h = 0 (Dijkstra): {len(dij_path) - 1} steps, "
          f"{dij_expanded} cells expanded")
    print(f"same cost: {len(path) == len(dij_path)}")

    # Edge cases: start equals goal, and a goal walled off completely.
    print(f"start == goal: {a_star(grid, start, start)[0]}")
    walled = ["...#...", "...#...", "...#..."]
    print(f"unreachable: {a_star(walled, (0, 0), (0, 6))[0]}")

    # An inadmissible heuristic overestimates: it explores far less, but the
    # optimality guarantee is gone, so a longer path may come back instead.
    # It happens to stay optimal on this maze; on another one it would not.
    def greedy(a: Cell, b: Cell) -> int:
        return 5 * manhattan(a, b)

    bad_path, bad_expanded = a_star(grid, start, goal, greedy)
    assert bad_path is not None
    print(f"inflated heuristic: {len(bad_path) - 1} steps, "
          f"{bad_expanded} cells expanded")


if __name__ == "__main__":
    main()
