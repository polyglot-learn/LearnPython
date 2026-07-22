"""Consistent hashing: spreading keys over nodes so that resizing is cheap.

With plain `hash(key) % n` every key's owner depends on n, so changing the
number of nodes remaps almost every key — a cache stampede or a full data
reshuffle. Consistent hashing instead places nodes and keys on the same
circular hash space and gives a key to the first node clockwise of it. Adding
or removing a node only disturbs the arc it owns, so roughly K/N keys move.

One node per point on the ring gives a lumpy distribution, because random
points are not evenly spaced. Virtual nodes fix this: each physical node is
hashed onto V points, and averaging V arcs shrinks the imbalance by about
sqrt(V). Lookup is a binary search over the sorted ring, so O(log(N*V)).
"""

import bisect
import hashlib
import random


def _hash(value: str) -> int:
    """A stable hash — Python's built-in hash() is salted per process."""
    return int.from_bytes(hashlib.md5(value.encode()).digest()[:8], "big")


class HashRing:
    def __init__(self, nodes: list[str] | None = None, replicas: int = 100) -> None:
        self.replicas = replicas
        self._ring: dict[int, str] = {}
        self._sorted: list[int] = []
        for node in nodes or []:
            self.add(node)

    def add(self, node: str) -> None:
        for i in range(self.replicas):
            point = _hash(f"{node}#{i}")
            self._ring[point] = node
            bisect.insort(self._sorted, point)

    def remove(self, node: str) -> None:
        for i in range(self.replicas):
            point = _hash(f"{node}#{i}")
            del self._ring[point]
            self._sorted.pop(bisect.bisect_left(self._sorted, point))

    def get(self, key: str) -> str | None:
        if not self._sorted:
            return None
        # First point clockwise; wrap to index 0 past the end of the ring.
        idx = bisect.bisect(self._sorted, _hash(key)) % len(self._sorted)
        return self._ring[self._sorted[idx]]


def modulo_owner(key: str, nodes: list[str]) -> str:
    return nodes[_hash(key) % len(nodes)]


def distribution(ring: HashRing, keys: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for key in keys:
        owner = ring.get(key)
        assert owner is not None
        counts[owner] = counts.get(owner, 0) + 1
    return counts


def imbalance(counts: dict[str, int]) -> float:
    """Worst bucket as a multiple of the ideal even share."""
    ideal = sum(counts.values()) / len(counts)
    return max(counts.values()) / ideal


def main() -> None:
    rng = random.Random(7)
    nodes = [f"node-{i}" for i in range(5)]
    keys = [f"key-{rng.randrange(10**9)}" for _ in range(20_000)]

    for replicas in (1, 10, 200):
        ring = HashRing(nodes, replicas=replicas)
        counts = distribution(ring, keys)
        share = sorted(round(100 * c / len(keys), 1) for c in counts.values())
        print(f"replicas={replicas:>3}: share% {share} "
              f"worst/ideal {imbalance(counts):.2f}")

    ring = HashRing(nodes, replicas=200)
    before = {k: ring.get(k) for k in keys}

    ring.add("node-5")
    moved = sum(1 for k in keys if ring.get(k) != before[k])
    print(f"\nadd a 6th node:    {moved / len(keys):>6.1%} of keys moved "
          f"(K/N ideal {1 / 6:.1%})")

    ring.remove("node-5")
    back = sum(1 for k in keys if ring.get(k) != before[k])
    print(f"remove it again:   {back / len(keys):>6.1%} of keys moved "
          "(ring returns to its earlier state)")

    ring.remove("node-4")
    moved = sum(1 for k in keys if ring.get(k) != before[k])
    print(f"remove a 5th node: {moved / len(keys):>6.1%} of keys moved "
          f"(K/N ideal {1 / 5:.1%})")

    old, new = nodes, nodes + ["node-5"]
    remapped = sum(1 for k in keys if modulo_owner(k, old) != modulo_owner(k, new))
    print(f"\nplain modulo 5->6: {remapped / len(keys):>6.1%} of keys remapped")

    # Edge cases: an empty ring owns nothing, and one node owns everything.
    print(f"\nempty ring lookup: {HashRing([]).get('anything')}")
    single = HashRing(["solo"], replicas=3)
    print(f"single-node ring:  {set(single.get(k) for k in keys[:100])}")


if __name__ == "__main__":
    main()
