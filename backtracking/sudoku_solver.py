"""Sudoku: constraint propagation first, backtracking only where it is needed.

The board is 81 cells, each needing a digit 1-9 such that every row, column and
3x3 box holds each digit once. Blind backtracking over 9 choices per empty cell
would explore an absurd tree, so the solver does two cheap things first.

Constraint propagation: repeatedly scan for a cell whose candidate set has
exactly one member and fill it in, which shrinks its neighbours' candidate sets,
which may create more singletons. On easy puzzles this alone solves the grid.

Minimum-remaining-values ordering: when propagation stalls, branch on the empty
cell with the fewest candidates. Failing fast on a 2-way choice prunes far more
than failing slowly on a 9-way one, and a cell with zero candidates aborts the
branch immediately.

Candidate sets are kept as per-row, per-column and per-box bitmasks, so testing
and updating a cell is a handful of integer operations. Worst case is still
exponential, but real puzzles solve in milliseconds.
"""

Grid = list[list[int]]

PUZZLE: Grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

HARD: Grid = [
    [8, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 3, 6, 0, 0, 0, 0, 0],
    [0, 7, 0, 0, 9, 0, 2, 0, 0],
    [0, 5, 0, 0, 0, 7, 0, 0, 0],
    [0, 0, 0, 0, 4, 5, 7, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 3, 0],
    [0, 0, 1, 0, 0, 0, 0, 6, 8],
    [0, 0, 8, 5, 0, 0, 0, 1, 0],
    [0, 9, 0, 0, 0, 0, 4, 0, 0],
]

ALL_DIGITS = 0b1111111110  # bits 1..9 set; bit 0 is unused so digits index directly


class Sudoku:
    def __init__(self, grid: Grid) -> None:
        self.grid = [row[:] for row in grid]
        self.rows = [0] * 9
        self.cols = [0] * 9
        self.boxes = [0] * 9
        for r in range(9):
            for c in range(9):
                if self.grid[r][c]:
                    self._place(r, c, self.grid[r][c])

    @staticmethod
    def _box(r: int, c: int) -> int:
        return (r // 3) * 3 + c // 3

    def _place(self, r: int, c: int, d: int) -> None:
        bit = 1 << d
        self.rows[r] |= bit
        self.cols[c] |= bit
        self.boxes[self._box(r, c)] |= bit
        self.grid[r][c] = d

    def _unplace(self, r: int, c: int, d: int) -> None:
        bit = 1 << d
        self.rows[r] &= ~bit
        self.cols[c] &= ~bit
        self.boxes[self._box(r, c)] &= ~bit
        self.grid[r][c] = 0

    def candidates(self, r: int, c: int) -> int:
        used = self.rows[r] | self.cols[c] | self.boxes[self._box(r, c)]
        return ALL_DIGITS & ~used

    def propagate(self) -> tuple[bool, list[tuple[int, int, int]]]:
        """Fill forced cells. Returns (still consistent, cells filled)."""
        filled: list[tuple[int, int, int]] = []
        progress = True
        while progress:
            progress = False
            for r in range(9):
                for c in range(9):
                    if self.grid[r][c]:
                        continue
                    cand = self.candidates(r, c)
                    if cand == 0:
                        return False, filled
                    if cand & (cand - 1) == 0:  # exactly one bit set
                        d = cand.bit_length() - 1
                        self._place(r, c, d)
                        filled.append((r, c, d))
                        progress = True
        return True, filled

    def _best_cell(self) -> tuple[int, int, int] | None:
        """Empty cell with fewest candidates, or None when the grid is full."""
        best: tuple[int, int, int] | None = None
        best_count = 10
        for r in range(9):
            for c in range(9):
                if self.grid[r][c]:
                    continue
                cand = self.candidates(r, c)
                count = cand.bit_count()
                if count < best_count:
                    best, best_count = (r, c, cand), count
                    if count <= 1:
                        return best
        return best

    def solve(self) -> bool:
        ok, filled = self.propagate()
        if not ok:
            for r, c, d in filled:
                self._unplace(r, c, d)
            return False
        cell = self._best_cell()
        if cell is None:
            return True
        r, c, cand = cell
        for d in range(1, 10):
            if not cand >> d & 1:
                continue
            self._place(r, c, d)
            if self.solve():
                return True
            self._unplace(r, c, d)
        for r2, c2, d2 in filled:  # undo propagation before reporting failure
            self._unplace(r2, c2, d2)
        return False


def render(grid: Grid) -> str:
    lines = []
    for r in range(9):
        if r and r % 3 == 0:
            lines.append("------+-------+------")
        cells = [str(v) if v else "." for v in grid[r]]
        lines.append(f"{' '.join(cells[:3])} | {' '.join(cells[3:6])} | "
                     f"{' '.join(cells[6:])}")
    return "\n".join(lines)


def is_solved(grid: Grid) -> bool:
    full = set(range(1, 10))
    boxes = [
        {grid[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)}
        for br in (0, 3, 6) for bc in (0, 3, 6)
    ]
    return (
        all(set(row) == full for row in grid)
        and all({grid[r][c] for r in range(9)} == full for c in range(9))
        and all(b == full for b in boxes)
    )


def main() -> None:
    print("puzzle:")
    print(render(PUZZLE))

    s = Sudoku(PUZZLE)
    solved = s.solve()
    print(f"\nsolved: {solved}, valid: {is_solved(s.grid)}")
    print(render(s.grid))

    # Propagation alone gets a long way on this puzzle before any guessing.
    probe = Sudoku(PUZZLE)
    ok, filled = probe.propagate()
    print(f"\nconstraint propagation alone filled {len(filled)} of "
          f"{sum(row.count(0) for row in PUZZLE)} empty cells (consistent={ok})")

    h = Sudoku(HARD)
    print(f"\n'world's hardest' puzzle solved: {h.solve()}, "
          f"valid: {is_solved(h.grid)}")
    print(render(h.grid))

    # An already-full grid needs no search; an inconsistent one fails cleanly.
    print(f"\nre-solving a finished grid: {Sudoku(s.grid).solve()}")
    broken = [row[:] for row in PUZZLE]
    broken[0][2] = 5  # duplicate 5 in the first row
    print(f"contradictory grid solvable: {Sudoku(broken).solve()}")


if __name__ == "__main__":
    main()
