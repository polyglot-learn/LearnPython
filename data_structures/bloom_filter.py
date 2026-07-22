"""Bloom filter: constant-space membership with one-sided error.

A bit array plus k hash functions. Adding sets k bits; querying checks them.
"Not present" is *certain*; "present" is probable — a false positive happens
when other insertions happened to set all k bits. There are no false negatives,
and elements cannot be removed (clearing a bit could unset a shared one).

For n items and m bits, the optimal k is (m/n)·ln2, giving a false-positive
rate of about (1 - e^(-kn/m))^k. Used as a cheap guard in front of an
expensive lookup: databases, CDNs, and crawlers all do this.
"""

import hashlib
import math


class BloomFilter:
    def __init__(self, expected: int, error_rate: float = 0.01) -> None:
        self.bits = self._optimal_bits(expected, error_rate)
        self.hashes = self._optimal_hashes(self.bits, expected)
        self.array = bytearray((self.bits + 7) // 8)
        self.added = 0

    @staticmethod
    def _optimal_bits(n: int, p: float) -> int:
        return max(8, int(-n * math.log(p) / (math.log(2) ** 2)))

    @staticmethod
    def _optimal_hashes(m: int, n: int) -> int:
        return max(1, round(m / n * math.log(2)))

    def _indices(self, item: str):
        """Kirsch-Mitzenmacher: derive k hashes from two, with no quality loss."""
        digest = hashlib.sha256(item.encode()).digest()
        h1 = int.from_bytes(digest[:8], "big")
        h2 = int.from_bytes(digest[8:16], "big") | 1
        for i in range(self.hashes):
            yield (h1 + i * h2) % self.bits

    def add(self, item: str) -> None:
        for index in self._indices(item):
            self.array[index // 8] |= 1 << (index % 8)
        self.added += 1

    def __contains__(self, item: str) -> bool:
        return all(
            self.array[i // 8] & (1 << (i % 8)) for i in self._indices(item)
        )

    def estimated_error_rate(self) -> float:
        return (1 - math.exp(-self.hashes * self.added / self.bits)) ** self.hashes


def main() -> None:
    bloom = BloomFilter(expected=1000, error_rate=0.01)
    print(f"{bloom.bits} bits ({len(bloom.array)} bytes), {bloom.hashes} hash functions")

    words = [f"word{i}" for i in range(1000)]
    for word in words:
        bloom.add(word)

    print(f"'word0' in filter:   {'word0' in bloom}   (true positive)")
    print(f"'word999' in filter: {'word999' in bloom}")
    print("no false negatives ever:",
          all(w in bloom for w in words))

    absent = [f"absent{i}" for i in range(10_000)]
    false_positives = sum(1 for w in absent if w in bloom)
    print(f"false positives: {false_positives}/10000 = {false_positives / 100:.2f}%")
    print(f"predicted rate: {bloom.estimated_error_rate() * 100:.2f}%")

    # Space comparison against storing the strings.
    exact = set(words)
    import sys

    print(f"set of 1000 strings: ~{sys.getsizeof(exact)} bytes just for the table")
    print(f"bloom filter:        {len(bloom.array)} bytes total")
    print("deletion is impossible — a cleared bit may belong to another item")


if __name__ == "__main__":
    main()
