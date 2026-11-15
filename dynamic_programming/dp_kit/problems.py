"""Classic dynamic-programming problems, each returning the answer and, where
useful, the actual solution (not just its size)."""

from bisect import bisect_left
from collections.abc import Sequence


def knapsack(weights: Sequence[int], values: Sequence[int], capacity: int) -> tuple[int, list[int]]:
    """0/1 knapsack. Returns (best value, chosen item indexes)."""
    n = len(weights)
    table = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(capacity + 1):
            table[i][c] = table[i - 1][c]
            if w <= c:
                table[i][c] = max(table[i][c], table[i - 1][c - w] + v)
    chosen, c = [], capacity
    for i in range(n, 0, -1):
        if table[i][c] != table[i - 1][c]:
            chosen.append(i - 1)
            c -= weights[i - 1]
    return table[n][capacity], sorted(chosen)


def lcs(a: str, b: str) -> str:
    """Longest common subsequence (one of them)."""
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            table[i][j] = (table[i + 1][j + 1] + 1 if a[i] == b[j]
                           else max(table[i + 1][j], table[i][j + 1]))
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append(a[i])
            i += 1
            j += 1
        elif table[i + 1][j] >= table[i][j + 1]:
            i += 1
        else:
            j += 1
    return "".join(out)


def edit_distance(a: str, b: str) -> int:
    """Levenshtein distance with a rolling row."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def coin_change(coins: Sequence[int], amount: int) -> list[int] | None:
    """Fewest coins summing to ``amount`` (the coins themselves), or None."""
    best: list[int | None] = [None] * (amount + 1)
    best[0] = 0
    last = [0] * (amount + 1)
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and best[a - c] is not None and (best[a] is None or best[a - c] + 1 < best[a]):
                best[a], last[a] = best[a - c] + 1, c
    if best[amount] is None:
        return None
    out = []
    while amount:
        out.append(last[amount])
        amount -= last[amount]
    return sorted(out, reverse=True)


def lis(nums: Sequence[int]) -> list[int]:
    """Longest strictly increasing subsequence in O(n log n)."""
    tails: list[int] = []  # tails[k] = index of smallest tail of a length k+1 run
    parent = [-1] * len(nums)
    for i, x in enumerate(nums):
        pos = bisect_left([nums[t] for t in tails], x)
        if pos:
            parent[i] = tails[pos - 1]
        if pos == len(tails):
            tails.append(i)
        else:
            tails[pos] = i
    out, i = [], tails[-1] if tails else -1
    while i != -1:
        out.append(nums[i])
        i = parent[i]
    return out[::-1]


def count_paths(rows: int, cols: int, blocked: set[tuple[int, int]] | None = None) -> int:
    """Monotone (right/down) paths across a grid, avoiding blocked cells."""
    blocked = blocked or set()
    ways = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if (r, c) in blocked:
                continue
            if r == c == 0:
                ways[r][c] = 1
            else:
                ways[r][c] = (ways[r - 1][c] if r else 0) + (ways[r][c - 1] if c else 0)
    return ways[-1][-1]
