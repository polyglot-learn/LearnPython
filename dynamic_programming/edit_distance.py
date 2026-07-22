"""Edit distance (Levenshtein): fewest single-character edits turning one string
into another, where an edit is an insertion, a deletion or a substitution.

The state is dist[i][j], the cost of turning the first i characters of a into
the first j characters of b. If the two characters at the end match, nothing
needs doing and the cost is dist[i-1][j-1]. Otherwise pay one edit and take the
cheapest of the three predecessors: dist[i-1][j] is a deletion from a,
dist[i][j-1] an insertion into a, dist[i-1][j-1] a substitution.

The base cases are the only non-obvious part: dist[i][0] is i, because emptying
a prefix costs one deletion per character, and dist[0][j] is j symmetrically.
Recording which predecessor won lets the edit script be replayed. Since each
row depends only on the previous one, the length can be computed in
O(min(m, n)) space by keeping the shorter string on the inner axis.

Complexity: O(m * n) time, O(m * n) space with the table and O(min(m, n))
without it.
"""


def edit_distance_table(a: str, b: str) -> list[list[int]]:
    m, n = len(a), len(b)
    dist = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dist[i][0] = i
    for j in range(n + 1):
        dist[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dist[i][j] = dist[i - 1][j - 1]
            else:
                dist[i][j] = 1 + min(dist[i - 1][j],      # delete a[i-1]
                                     dist[i][j - 1],      # insert b[j-1]
                                     dist[i - 1][j - 1])  # substitute
    return dist


def edit_distance(a: str, b: str) -> int:
    return edit_distance_table(a, b)[len(a)][len(b)]


def edit_distance_small_space(a: str, b: str) -> int:
    """Two rows only, with the shorter string driving the row width."""
    if len(b) > len(a):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i] + [0] * len(b)
        for j, cb in enumerate(b, start=1):
            if ca == cb:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev = curr
    return prev[len(b)]


def edit_script(a: str, b: str) -> list[str]:
    """One shortest sequence of operations, read back out of the table."""
    dist = edit_distance_table(a, b)
    steps: list[str] = []
    i, j = len(a), len(b)
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
            steps.append(f"keep {a[i - 1]!r}")
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and dist[i][j] == dist[i - 1][j - 1] + 1:
            steps.append(f"substitute {a[i - 1]!r} -> {b[j - 1]!r}")
            i, j = i - 1, j - 1
        elif i > 0 and dist[i][j] == dist[i - 1][j] + 1:
            steps.append(f"delete {a[i - 1]!r}")
            i -= 1
        else:
            steps.append(f"insert {b[j - 1]!r}")
            j -= 1
    steps.reverse()
    return steps


def main() -> None:
    pairs = [
        ("kitten", "sitting"),
        ("flaw", "lawn"),
        ("intention", "execution"),
        ("sunday", "saturday"),
    ]
    for a, b in pairs:
        d = edit_distance(a, b)
        print(f"{a!r} -> {b!r}: {d}")
        assert edit_distance_small_space(a, b) == d

    print("\nedit script for 'kitten' -> 'sitting':")
    for step in edit_script("kitten", "sitting"):
        print("  " + step)

    print("\nedge cases:")
    print("  '' -> 'abc':      ", edit_distance("", "abc"))
    print("  'abc' -> '':      ", edit_distance("abc", ""))
    print("  '' -> '':         ", edit_distance("", ""))
    print("  identical strings:", edit_distance("same", "same"))
    print("  no shared letters:", edit_distance("abc", "xyz"))


if __name__ == "__main__":
    main()
