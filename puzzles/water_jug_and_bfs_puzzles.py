"""Puzzles as graph search: states are nodes, moves are edges, BFS finds the
shortest solution.

The water jug problem, the missionaries-and-cannibals problem and the sliding
tile puzzle look nothing alike, yet each reduces to the same three questions:
what is a state, what moves are legal from it, and which states are goals.
Answer those and breadth-first search returns the minimum number of moves for
free, because BFS explores in order of depth.

The visited set is what keeps it finite — without it, the jugs would pour back
and forth forever. Complexity is O(states * moves-per-state).
"""

from collections import deque
from collections.abc import Callable, Iterable


def bfs_solve[S](
    start: S,
    is_goal: Callable[[S], bool],
    moves: Callable[[S], Iterable[S]],
) -> list[S] | None:
    """Shortest path in state space, returned as the sequence of states."""
    if is_goal(start):
        return [start]
    queue: deque[S] = deque([start])
    parent: dict[S, S | None] = {start: None}
    while queue:
        state = queue.popleft()
        for nxt in moves(state):
            if nxt in parent:
                continue
            parent[nxt] = state
            if is_goal(nxt):
                path = [nxt]
                while parent[path[-1]] is not None:
                    path.append(parent[path[-1]])
                return list(reversed(path))
            queue.append(nxt)
    return None


def jug_moves(capacity: tuple[int, int]):
    cap_a, cap_b = capacity

    def moves(state: tuple[int, int]) -> list[tuple[int, int]]:
        a, b = state
        pour_ab = min(a, cap_b - b)
        pour_ba = min(b, cap_a - a)
        return [
            (cap_a, b),            # fill A
            (a, cap_b),            # fill B
            (0, b),                # empty A
            (a, 0),                # empty B
            (a - pour_ab, b + pour_ab),  # A -> B
            (a + pour_ba, b - pour_ba),  # B -> A
        ]

    return moves


def missionaries_moves(state: tuple[int, int, int]) -> list[tuple[int, int, int]]:
    """(missionaries, cannibals, boat) on the starting bank; 3 of each, boat holds 2."""
    m, c, boat = state
    out: list[tuple[int, int, int]] = []
    direction = -1 if boat == 1 else 1
    for dm, dc in ((1, 0), (2, 0), (0, 1), (0, 2), (1, 1)):
        nm, nc = m + direction * dm, c + direction * dc
        if not (0 <= nm <= 3 and 0 <= nc <= 3):
            continue
        # Missionaries must never be outnumbered on either bank.
        if (nm and nm < nc) or ((3 - nm) and (3 - nm) < (3 - nc)):
            continue
        out.append((nm, nc, 1 - boat))
    return out


def main() -> None:
    print("water jugs: 4-litre and 3-litre, measure exactly 2 litres")
    path = bfs_solve((0, 0), lambda s: 2 in s, jug_moves((4, 3)))
    for step, state in enumerate(path):
        print(f"  {step}: jugs {state}")
    print(f"  solved in {len(path) - 1} moves")

    print("unsolvable when the target is not a multiple of gcd(capacities):")
    print(f"  measure 3 with 4- and 6-litre jugs -> "
          f"{bfs_solve((0, 0), lambda s: 3 in s, jug_moves((4, 6)))}")

    print("missionaries and cannibals (3 each, boat holds 2):")
    solution = bfs_solve((3, 3, 1), lambda s: s == (0, 0, 0), missionaries_moves)
    print(f"  shortest solution: {len(solution) - 1} crossings")
    for step, (m, c, boat) in enumerate(solution):
        side = "start" if boat else "far"
        print(f"  {step}: {m}M {c}C on the start bank, boat at the {side} bank")

    print("the same solver, three problems — state, moves, goal is the whole interface")


if __name__ == "__main__":
    main()
