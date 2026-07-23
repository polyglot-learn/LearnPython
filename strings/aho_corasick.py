"""Aho-Corasick: find every occurrence of a whole set of patterns in one pass.

Build a trie of the patterns, then add "failure links". A failure link points
from a node to the node representing the longest proper suffix of the current
matched prefix that is also a prefix of some pattern — the exact generalisation
of KMP's failure function to many patterns. The links are filled in by a BFS,
because a node's failure target is always shallower and thus already known.

Scanning the text, each character either follows a normal edge or, on a miss,
walks failure links until an edge exists. Every node also carries an "output"
list (its own patterns plus those reachable via failure links) so all patterns
ending at a position are reported. Total work is O(text + patterns + matches).
"""

from collections import deque


class AhoCorasick:
    def __init__(self, patterns: list[str]) -> None:
        self.goto: list[dict[str, int]] = [{}]
        self.fail: list[int] = [0]
        self.output: list[list[str]] = [[]]
        for p in patterns:
            self._add(p)
        self._build_links()

    def _add(self, word: str) -> None:
        node = 0
        for ch in word:
            if ch not in self.goto[node]:
                self.goto[node][ch] = len(self.goto)
                self.goto.append({})
                self.fail.append(0)
                self.output.append([])
            node = self.goto[node][ch]
        self.output[node].append(word)

    def _build_links(self) -> None:
        queue: deque[int] = deque()
        for child in self.goto[0].values():
            queue.append(child)  # depth-1 nodes fail back to the root
        while queue:
            node = queue.popleft()
            for ch, child in self.goto[node].items():
                queue.append(child)
                f = self.fail[node]
                while f and ch not in self.goto[f]:
                    f = self.fail[f]  # walk failure links until edge exists
                target = self.goto[f].get(ch, 0)
                self.fail[child] = target if target != child else 0
                # inherit outputs reachable through the failure link
                self.output[child] += self.output[self.fail[child]]

    def find(self, text: str) -> list[tuple[int, str]]:
        """(end_index, pattern) for every match; end_index is inclusive."""
        node = 0
        hits: list[tuple[int, str]] = []
        for i, ch in enumerate(text):
            while node and ch not in self.goto[node]:
                node = self.fail[node]
            node = self.goto[node].get(ch, 0)
            for word in self.output[node]:
                hits.append((i, word))
        return hits


def naive_find(text: str, patterns: list[str]) -> list[tuple[int, str]]:
    out = []
    for p in patterns:
        start = text.find(p)
        while p and start != -1:
            out.append((start + len(p) - 1, p))
            start = text.find(p, start + 1)
    return sorted(out)


def main() -> None:
    patterns = ["he", "she", "his", "hers"]
    ac = AhoCorasick(patterns)
    text = "ushers"
    matches = sorted(ac.find(text))
    print(f"text = {text!r}, patterns = {patterns}")
    for end, word in matches:
        print(f"  {word!r} ends at index {end} (starts at {end - len(word) + 1})")

    # Cross-check against the naive per-pattern search on several texts.
    trials = [
        ("ushers", ["he", "she", "his", "hers"]),
        ("abababab", ["ab", "bab", "abab"]),
        ("aaaa", ["a", "aa", "aaa"]),
        ("mississippi", ["is", "issi", "ppi", "xyz"]),
    ]
    for txt, pats in trials:
        got = sorted(AhoCorasick(pats).find(txt))
        want = naive_find(txt, pats)
        assert got == want, (txt, pats, got, want)
    print("all matches agree with naive search")


if __name__ == "__main__":
    main()
