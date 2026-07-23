"""Suffix array: the sorted order of all suffixes, given as their start indices.

Sorting suffixes naively costs O(n^2 log n) because each comparison scans whole
suffixes. Prefix-doubling avoids that: rank the suffixes by their first
character, then repeatedly by their first 2, 4, 8, ... characters. Each round
sorts pairs (rank of this position, rank 2^k ahead), which are integers, so a
round is O(n log n) and there are log n rounds — O(n log^2 n) overall.

Kasai's algorithm then computes the LCP array (longest common prefix between
each suffix and the previous one in sorted order) in O(n), exploiting that
adjacent suffixes lose at most one leading character as you step through the
text. With the suffix array a substring search is a binary search in O(m log n).
"""


def build_suffix_array(s: str) -> list[int]:
    n = len(s)
    sa = list(range(n))
    rank = [ord(c) for c in s]
    tmp = [0] * n
    k = 1
    while k < n:
        def key(i: int) -> tuple[int, int]:
            second = rank[i + k] if i + k < n else -1
            return (rank[i], second)

        sa.sort(key=key)
        tmp[sa[0]] = 0
        for i in range(1, n):
            tmp[sa[i]] = tmp[sa[i - 1]] + (key(sa[i]) != key(sa[i - 1]))
        rank = tmp[:]
        if rank[sa[-1]] == n - 1:  # all ranks distinct, fully sorted
            break
        k *= 2
    return sa


def build_lcp(s: str, sa: list[int]) -> list[int]:
    """Kasai's algorithm: lcp[i] = LCP(suffix sa[i-1], suffix sa[i]); lcp[0]=0."""
    n = len(s)
    rank = [0] * n
    for i, suf in enumerate(sa):
        rank[suf] = i
    lcp = [0] * n
    h = 0
    for i in range(n):
        if rank[i] == 0:
            h = 0
            continue
        j = sa[rank[i] - 1]  # suffix just before i in sorted order
        while i + h < n and j + h < n and s[i + h] == s[j + h]:
            h += 1
        lcp[rank[i]] = h
        if h:
            h -= 1  # next suffix drops one leading char, so LCP falls by <=1
    return lcp


def sa_contains(s: str, sa: list[int], pattern: str) -> bool:
    lo, hi = 0, len(sa)
    while lo < hi:
        mid = (lo + hi) // 2
        if s[sa[mid]:] < pattern:
            lo = mid + 1
        else:
            hi = mid
    return lo < len(sa) and s[sa[lo]:].startswith(pattern)


def main() -> None:
    s = "banana"
    sa = build_suffix_array(s)
    print(f"suffix array of '{s}': {sa}")
    print("sorted suffixes: " + ", ".join(s[i:] for i in sa))
    print(f"lcp array: {build_lcp(s, sa)}")

    for p in ["ana", "nan", "ban", "x", "banana", "a"]:
        print(f"contains('{p}'): {sa_contains(s, sa, p)}  (str: {p in s})")

    # Cross-check the suffix array against Python's own suffix sort.
    for text in ["mississippi", "aaaaa", "abracadabra", "z", "abcabcabc"]:
        got = build_suffix_array(text)
        want = sorted(range(len(text)), key=lambda i: text[i:])
        assert got == want, (text, got, want)
    print("suffix arrays match brute-force sort on all cases")


if __name__ == "__main__":
    main()
