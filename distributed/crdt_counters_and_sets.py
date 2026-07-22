"""CRDTs: replicas that converge no matter what order updates arrive in.

A state-based CRDT is a value plus a merge function that is commutative,
associative and idempotent. Those three properties are exactly what you need
when the network can reorder, duplicate and redeliver messages: replaying an
old message changes nothing, and two replicas that have seen the same set of
updates hold the same state regardless of the order they saw them in. That is
strong eventual convergence with no coordination and no conflict resolution.

A G-Counter keeps one per-replica tally and merges by taking the element-wise
maximum; the value is the sum. An OR-Set tags each add with a unique token and
a remove tombstones only the tokens it observed, so a concurrent add-and-remove
resolves as add-wins and a re-add after a remove survives.
"""

import random
from collections.abc import Hashable
from dataclasses import dataclass, field
from itertools import count

_tokens = count()  # stands in for a (replica id, sequence) unique tag


@dataclass
class GCounter:
    """Grow-only counter. Decrements need two G-Counters (a PN-Counter)."""

    counts: dict[str, int] = field(default_factory=dict)

    def increment(self, replica: str, amount: int = 1) -> None:
        if amount < 0:
            raise ValueError("a G-Counter only grows")
        self.counts[replica] = self.counts.get(replica, 0) + amount

    def merge(self, other: "GCounter") -> "GCounter":
        keys = self.counts.keys() | other.counts.keys()
        return GCounter({k: max(self.counts.get(k, 0), other.counts.get(k, 0))
                         for k in keys})

    def value(self) -> int:
        return sum(self.counts.values())


@dataclass
class ORSet[T: Hashable]:
    """Observed-remove set: (element, unique tag) pairs plus tombstoned tags."""

    entries: set[tuple[T, int]] = field(default_factory=set)
    removed: set[int] = field(default_factory=set)

    def add(self, item: T) -> None:
        self.entries.add((item, next(_tokens)))

    def remove(self, item: T) -> None:
        # Only tags this replica has actually observed are tombstoned, so a
        # concurrent add elsewhere carries a tag we never saw and survives.
        self.removed |= {tag for element, tag in self.entries if element == item}

    def merge(self, other: "ORSet[T]") -> "ORSet[T]":
        return ORSet(self.entries | other.entries, self.removed | other.removed)

    def value(self) -> set[T]:
        return {e for e, tag in self.entries if tag not in self.removed}


def main() -> None:
    rng = random.Random(11)

    print("G-Counter: three replicas count page views offline")
    a, b, c = GCounter(), GCounter(), GCounter()
    a.increment("a", 5)
    b.increment("b", 3)
    c.increment("c", 7)
    print(f"  local values: a={a.value()} b={b.value()} c={c.value()}")

    updates = [a, b, c]
    for trial in range(3):
        order = updates[:]
        rng.shuffle(order)
        gossiped = GCounter()
        for upd in order + order:  # deliver everything twice: idempotence
            gossiped = gossiped.merge(upd)
        names = "".join(sorted(u.counts)[0] for u in order)
        print(f"  shuffle {trial} order {names} (each twice) -> {gossiped.value()}")

    print("\n  merging a replica with itself is a no-op: "
          f"{a.merge(a).counts == a.counts}")
    print(f"  empty counter value: {GCounter().value()}")
    try:
        a.increment("a", -1)
    except ValueError as exc:
        print(f"  negative increment rejected: {exc}")

    print("\nOR-Set: a shopping cart edited on phone and laptop")
    phone: ORSet[str] = ORSet()
    for item in ("milk", "bread", "eggs"):
        phone.add(item)
    laptop = phone.merge(ORSet())  # laptop syncs, then both go offline

    laptop.remove("bread")
    phone.add("bread")  # concurrent re-add carries a tag laptop never saw
    laptop.add("jam")
    phone.remove("eggs")

    print(f"  phone:  {sorted(phone.value())}")
    print(f"  laptop: {sorted(laptop.value())}")
    left, right = phone.merge(laptop), laptop.merge(phone)
    print(f"  merged either way: {sorted(left.value())} "
          f"(commutative: {left.value() == right.value()})")
    print("  bread survived because the concurrent add was never observed "
          "by the remove")

    solo: ORSet[str] = ORSet()
    solo.add("temp")
    solo.remove("temp")
    print(f"\n  add then remove on one replica: {sorted(solo.value())}")
    solo.remove("ghost")  # removing something never added is a no-op
    print(f"  after removing an absent element: {sorted(solo.value())}")


if __name__ == "__main__":
    main()
