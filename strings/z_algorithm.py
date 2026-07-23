"""Z-algorithm: for each position, the longest substring starting there that
is also a prefix of the string — the whole Z-array in O(n).

The trick is a "Z-box": the interval [l, r] of the rightmost prefix-match seen
so far. Inside that box the string already equals its own prefix, so z[i] can be
copied from the earlier position z[i - l] instead of recomputed, and only the
part sticking out past r ever needs fresh character comparisons.

Pattern search falls out for free: run the Z-array over "pattern$text" and any
position whose Z-value equals len(pattern) marks a match in the text. The '$'
separator can never be part of the pattern, so matches never straddle it.
"""


def z_array(s: str) -> list[int]:
    n = len(s)
    z = [0] * n
    z[0] = n  # by convention the whole string matches its own prefix
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])  # copy inside the current Z-box
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:  # extended past the box, so re-anchor it
            l, r = i, i + z[i]
    return z


def z_search(text: str, pattern: str) -> list[int]:
    """All start indices where `pattern` occurs in `text`."""
    if not pattern:
        return list(range(len(text) + 1))
    combined = pattern + "\0" + text  # separator absent from both inputs
    z = z_array(combined)
    m = len(pattern)
    return [i - m - 1 for i in range(m + 1, len(combined)) if z[i] == m]


def main() -> None:
    print(f"z_array('aabxaabxcaabxaabxay') = {z_array('aabxaabxcaabxaabxay')}")
    print(f"z_array('aaaaa') = {z_array('aaaaa')}")

    text, pattern = "ababcabcabababd", "ababd"
    print(z_search(text, pattern))
    print(f"str.find agrees: {text.find(pattern)}")

    print(z_search("aaaaa", "aa"))  # overlapping matches
    print(z_search("abc", "xyz"))

    # Cross-check against str.find on a battery of cases.
    cases = [("mississippi", "issi"), ("aaaa", "a"), ("abcabc", "abc"),
             ("hello", ""), ("x", "xyz"), ("banana", "ana")]
    for t, p in cases:
        got = z_search(t, p)
        want = []
        start = t.find(p)
        while p and start != -1:
            want.append(start)
            start = t.find(p, start + 1)
        if not p:
            want = list(range(len(t) + 1))
        assert got == want, (t, p, got, want)
    print("all cross-checks against str.find passed")


if __name__ == "__main__":
    main()
