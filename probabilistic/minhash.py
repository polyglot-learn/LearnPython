"""MinHash: estimating how similar two sets are without comparing them.

Jaccard similarity is |A intersect B| / |A union B|. Computing it exactly means
holding both sets, which is fine for two documents and hopeless for a corpus of
millions where every pair might need checking.

The trick is a random permutation of the universe of elements. Under such a
permutation, the element that comes first in A and the element that comes first
in B are the same element exactly when that first-overall element of the union
also lies in the intersection — an event with probability precisely the Jaccard
similarity. So one permutation gives one unbiased Bernoulli sample of J.

Repeat with k independent hash functions, store only the k minima as a signature,
and estimate J as the fraction of positions where two signatures agree. The
standard error is about 1/sqrt(k), so 200 hashes give roughly 7% error, 1000 give
3%. Comparing two documents then costs O(k) regardless of their length, and the
signatures are small enough to keep in memory for a whole corpus.

Documents become sets by shingling: every contiguous run of n words or characters
becomes one element, so word order still matters.
"""

import math


FNV_OFFSET = 0xCBF29CE484222325
FNV_PRIME = 0x100000001B3
MASK64 = (1 << 64) - 1


def hash64(data: bytes, seed: int = FNV_OFFSET) -> int:
    """Seedable FNV-1a with an avalanche step; deterministic across runs."""
    h = seed
    for byte in data:
        h = ((h ^ byte) * FNV_PRIME) & MASK64
    h ^= h >> 33
    h = (h * 0xFF51AFD7ED558CCD) & MASK64
    h ^= h >> 29
    return h


def shingles(text: str, n: int = 3) -> set[str]:
    """Word n-grams; two texts sharing phrasing share shingles."""
    words = text.lower().split()
    if len(words) < n:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    union = len(a | b)
    if union == 0:
        return 1.0  # two empty sets are identical by convention
    return len(a & b) / union


class MinHash:
    def __init__(self, num_hashes: int = 200, seed: int = 1) -> None:
        if num_hashes <= 0:
            raise ValueError("num_hashes must be positive")
        self.num_hashes = num_hashes
        # Distinct seeds stand in for distinct random permutations.
        self.seeds = [hash64(str(seed).encode(), FNV_OFFSET + i)
                      for i in range(num_hashes)]

    def signature(self, items: set[str]) -> list[int]:
        sig = [MASK64] * self.num_hashes
        for item in items:
            data = item.encode()
            for i, s in enumerate(self.seeds):
                h = hash64(data, s)
                if h < sig[i]:
                    sig[i] = h
        return sig

    def similarity(self, sig_a: list[int], sig_b: list[int]) -> float:
        agree = sum(1 for x, y in zip(sig_a, sig_b) if x == y)
        return agree / self.num_hashes

    def standard_error(self) -> float:
        return 1 / math.sqrt(self.num_hashes)


DOCS = {
    "A": "the quick brown fox jumps over the lazy dog near the river bank",
    "B": "the quick brown fox leaps over the lazy dog near the river bank",
    "C": "a quick brown fox jumps over a lazy dog beside the river bank",
    "D": "grammars of programming languages describe the syntax of valid code",
    "E": "the quick brown fox jumps over the lazy dog near the river bank",
}


def main() -> None:
    sets = {name: shingles(text, 3) for name, text in DOCS.items()}
    for name in DOCS:
        print(f"document {name}: {len(sets[name])} shingles")

    mh = MinHash(num_hashes=256, seed=7)
    sigs = {name: mh.signature(s) for name, s in sets.items()}
    print(f"\n256 hashes, expected error about "
          f"{mh.standard_error() * 100:.1f}%")
    print("  pair   exact     estimate   difference")
    names = sorted(DOCS)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            exact = jaccard(sets[a], sets[b])
            est = mh.similarity(sigs[a], sigs[b])
            print(f"  {a}-{b}   {exact:.4f}    {est:.4f}     {est - exact:+.4f}")

    print("\nmore hashes, tighter estimates (pair A-B, exact "
          f"{jaccard(sets['A'], sets['B']):.4f})")
    for k in (16, 64, 256, 1024, 4096):
        m = MinHash(num_hashes=k, seed=7)
        est = m.similarity(m.signature(sets["A"]), m.signature(sets["B"]))
        exact = jaccard(sets["A"], sets["B"])
        print(f"  k = {k:>5}: estimate {est:.4f}, error {est - exact:+.4f}, "
              f"expected +-{m.standard_error():.4f}")

    # Averaging over seeds shows the estimator is unbiased, not merely close.
    print("\nunbiasedness: 40 independent 64-hash estimates of A-C")
    exact = jaccard(sets["A"], sets["C"])
    estimates = []
    for seed in range(40):
        m = MinHash(num_hashes=64, seed=seed)
        estimates.append(m.similarity(m.signature(sets["A"]),
                                      m.signature(sets["C"])))
    mean = sum(estimates) / len(estimates)
    spread = math.sqrt(sum((e - mean) ** 2 for e in estimates) / len(estimates))
    print(f"  exact {exact:.4f}, mean of estimates {mean:.4f}, "
          f"spread {spread:.4f}")
    print(f"  range {min(estimates):.4f} to {max(estimates):.4f}")

    print("\nshingle size changes what 'similar' means (A vs C)")
    for n in (1, 2, 3, 5):
        print(f"  {n}-grams: exact jaccard "
              f"{jaccard(shingles(DOCS['A'], n), shingles(DOCS['C'], n)):.4f}")

    print("\nedge cases")
    print(f"  identical documents A and E: exact "
          f"{jaccard(sets['A'], sets['E']):.4f}, "
          f"estimate {mh.similarity(sigs['A'], sigs['E']):.4f}")
    empty = mh.signature(set())
    print(f"  empty set signature is all-max: {set(empty) == {MASK64}}")
    print(f"  empty vs empty estimate: {mh.similarity(empty, empty):.4f}")
    print(f"  empty vs A estimate: {mh.similarity(empty, sigs['A']):.4f} "
          f"(exact {jaccard(set(), sets['A']):.4f})")
    print(f"  disjoint documents A and D: exact "
          f"{jaccard(sets['A'], sets['D']):.4f}, "
          f"estimate {mh.similarity(sigs['A'], sigs['D']):.4f}")
    print(f"  shingling a text shorter than n: {shingles('two words', 5)}")
    print(f"  shingling an empty text: {shingles('', 3)}")
    try:
        MinHash(0)
    except ValueError as exc:
        print(f"  zero hashes: ValueError({exc})")


if __name__ == "__main__":
    main()
