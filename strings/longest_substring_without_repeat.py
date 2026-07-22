"""Longest substring with no repeated character — the sliding window template.

Keep a window [start, i] and a map from character to its last index. When the
current character was seen *inside* the window, jump `start` past that
occurrence. The window never shrinks by more than it must, so every index is
visited once: O(n) time, O(k) space for an alphabet of size k.

The `last[ch] >= start` guard is the part people drop, which silently breaks
inputs like "abba".
"""


def longest_unique_substring(text: str) -> str:
    last: dict[str, int] = {}
    start = best_start = best_len = 0
    for i, ch in enumerate(text):
        if ch in last and last[ch] >= start:
            start = last[ch] + 1  # move past the earlier occurrence
        last[ch] = i
        if i - start + 1 > best_len:
            best_len = i - start + 1
            best_start = start
    return text[best_start:best_start + best_len]


def longest_with_at_most_k_distinct(text: str, k: int) -> str:
    """Same window, different invariant: at most k distinct characters."""
    counts: dict[str, int] = {}
    start = best_start = best_len = 0
    for i, ch in enumerate(text):
        counts[ch] = counts.get(ch, 0) + 1
        while len(counts) > k:
            left = text[start]
            counts[left] -= 1
            if counts[left] == 0:
                del counts[left]
            start += 1
        if i - start + 1 > best_len:
            best_len, best_start = i - start + 1, start
    return text[best_start:best_start + best_len]


def main() -> None:
    for s in ("abcabcbb", "bbbbb", "pwwkew", "abba", ""):
        print(f"{s!r:12} -> {longest_unique_substring(s)!r}")
    print(f"at most 2 distinct in 'eceba' -> {longest_with_at_most_k_distinct('eceba', 2)!r}")


if __name__ == "__main__":
    main()
