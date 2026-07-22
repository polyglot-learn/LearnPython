"""Conway's Game of Life: four rules, unbounded emergent behaviour.

A cell with two or three live neighbours survives; a dead cell with exactly
three is born; everything else dies. That is the entire specification, and it
is enough to build gliders, oscillators, and a Turing-complete machine.

The dense implementation scans a fixed grid: O(rows*cols) per generation
regardless of how empty it is. The sparse implementation stores only live
cells and considers only cells adjacent to one, which is O(live) — the right
choice for the large, mostly empty boards Life patterns actually produce.
"""

from collections import Counter

Cell = tuple[int, int]


def step_dense(grid: list[list[int]]) -> list[list[int]]:
    rows, cols = len(grid), len(grid[0])
    out = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            neighbours = sum(
                grid[r + dr][c + dc]
                for dr in (-1, 0, 1)
                for dc in (-1, 0, 1)
                if (dr or dc) and 0 <= r + dr < rows and 0 <= c + dc < cols
            )
            out[r][c] = int(neighbours == 3 or (grid[r][c] and neighbours == 2))
    return out


def step_sparse(live: set[Cell]) -> set[Cell]:
    """Only cells next to a live one can change, so only count those."""
    counts: Counter[Cell] = Counter()
    for r, c in live:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr or dc:
                    counts[(r + dr, c + dc)] += 1
    return {
        cell
        for cell, n in counts.items()
        if n == 3 or (n == 2 and cell in live)
    }


def render(live: set[Cell], rows: int, cols: int) -> str:
    return "\n".join(
        "".join("#" if (r, c) in live else "." for c in range(cols))
        for r in range(rows)
    )


def main() -> None:
    glider = {(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)}
    print("glider, generations 0-4 on a 6x6 window:")
    live = glider
    for generation in range(5):
        print(f"  gen {generation}:")
        for line in render(live, 6, 6).splitlines():
            print(f"    {line}")
        live = step_sparse(live)

    print("the glider has translated one cell diagonally after four steps:")
    shifted = {(r - 1, c - 1) for r, c in live}
    print(f"  same shape, offset by (1, 1): {shifted == glider}")

    print("blinker oscillates with period 2:")
    blinker = {(1, 0), (1, 1), (1, 2)}
    once = step_sparse(blinker)
    twice = step_sparse(once)
    print(f"  vertical after one step: {sorted(once)}")
    print(f"  back to the start: {twice == blinker}")

    print("block is a still life:")
    block = {(0, 0), (0, 1), (1, 0), (1, 1)}
    print(f"  unchanged: {step_sparse(block) == block}")

    print("dense and sparse agree:")
    grid = [[1 if (r, c) in glider else 0 for c in range(6)] for r in range(6)]
    dense_next = step_dense(grid)
    dense_live = {(r, c) for r in range(6) for c in range(6) if dense_next[r][c]}
    print(f"  {dense_live == step_sparse(glider)}")
    print("  (they diverge only at the dense grid's edges, which clip the pattern)")


if __name__ == "__main__":
    main()
