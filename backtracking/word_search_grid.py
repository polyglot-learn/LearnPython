"""Word search: find a word in a character grid by depth-first backtracking.

From every cell whose letter matches the first character, walk to the four
orthogonal neighbours looking for the next character. A cell may not be reused
within one path, so the walk needs a visited marker — and because the search
backtracks, the marker must be removed again when the path fails.

The idiom here is in-place marking: temporarily overwrite the visited cell with
a sentinel character that can never match, then restore the original letter on
the way out. It costs no extra memory beyond the recursion stack and makes the
"already on this path" test a plain character comparison. A separate visited set
is equally correct and is the right choice when the grid must not be mutated,
for instance when it is shared across threads.

Worst case is O(rows * cols * 4^len(word)): every start cell, times up to four
directions at each of the word's characters. In practice the character check
prunes almost everything immediately.
"""

Grid = list[list[str]]

VISITED = "\0"  # a character that can never appear in the word


def exists(board: Grid, word: str) -> bool:
    if not word:
        return True
    if not board or not board[0]:
        return False
    rows, cols = len(board), len(board[0])

    def dfs(r: int, c: int, k: int) -> bool:
        if k == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[k]:
            return False
        board[r][c] = VISITED
        found = (
            dfs(r + 1, c, k + 1) or dfs(r - 1, c, k + 1)
            or dfs(r, c + 1, k + 1) or dfs(r, c - 1, k + 1)
        )
        board[r][c] = word[k]  # restore before returning, success or not
        return found

    return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))


def find_path(board: Grid, word: str) -> list[tuple[int, int]] | None:
    """Same search, but returns the winning cell coordinates."""
    if not word or not board or not board[0]:
        return [] if word == "" else None
    rows, cols = len(board), len(board[0])
    path: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()

    def dfs(r: int, c: int, k: int) -> bool:
        if not (0 <= r < rows and 0 <= c < cols):
            return False
        if (r, c) in seen or board[r][c] != word[k]:
            return False
        seen.add((r, c))
        path.append((r, c))
        if k == len(word) - 1:
            return True
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if dfs(r + dr, c + dc, k + 1):
                return True
        seen.discard((r, c))
        path.pop()
        return False

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return path
    return None


def to_grid(rows: list[str]) -> Grid:
    return [list(row) for row in rows]


def main() -> None:
    board = to_grid(["ABCE", "SFCS", "ADEE"])
    for row in board:
        print(" ".join(row))

    for word in ["ABCCED", "SEE", "ABCB", "ASADFCE", ""]:
        print(f"exists({word!r}): {exists(board, word)}")

    print(f"path for 'ABCCED': {find_path(board, 'ABCCED')}")
    print(f"path for 'SEE':    {find_path(board, 'SEE')}")
    print(f"path for 'ABCB':   {find_path(board, 'ABCB')}")

    # The board must come back unchanged after all that in-place marking.
    print(f"board intact: {board == to_grid(['ABCE', 'SFCS', 'ADEE'])}")

    print(f"empty board: {exists([], 'A')}")
    print(f"single cell hit:  {exists(to_grid(['A']), 'A')}")
    print(f"single cell miss: {exists(to_grid(['A']), 'AA')}")

    # A worst case for the naive search: one repeated letter everywhere.
    stress = to_grid(["A" * 6 for _ in range(6)])
    print(f"'AAAAAAA' in all-A grid: {exists(stress, 'A' * 7)}")
    print(f"'AAAAAB'  in all-A grid: {exists(stress, 'A' * 5 + 'B')}")


if __name__ == "__main__":
    main()
