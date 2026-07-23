"""Skip list: a sorted linked list with express lanes, O(log n) expected.

Each node appears in level 0; with probability p (usually 1/2) it is also
promoted to level 1, and again to level 2, and so on. The upper levels are
sparse express lanes, so a search drops down from the top, skipping large
stretches at each level before descending — the same divide-and-conquer a
balanced tree gives, but achieved by randomness rather than rotations.

The appeal is simplicity: no rebalancing cases, and the same code powers
concurrent implementations (Java's ConcurrentSkipListMap, Redis sorted sets).

Search, insert and delete are O(log n) expected; the height is O(log n) with
high probability. Space is O(n) expected (each node's extra levels sum to
1/(1-p) on average).
"""

import random


class Node:
    __slots__ = ("key", "forward")

    def __init__(self, key: int, level: int) -> None:
        self.key = key
        self.forward: list[Node | None] = [None] * (level + 1)


class SkipList:
    def __init__(self, max_level: int = 16, p: float = 0.5, seed: int = 0) -> None:
        self.max_level = max_level
        self.p = p
        self.level = 0  # highest level currently in use
        self.head = Node(key=-(2**60), level=max_level)  # -infinity sentinel
        self._rng = random.Random(seed)

    def _random_level(self) -> int:
        level = 0
        while self._rng.random() < self.p and level < self.max_level:
            level += 1
        return level

    def insert(self, key: int) -> None:
        update = [self.head] * (self.max_level + 1)
        node = self.head
        for i in range(self.level, -1, -1):
            while node.forward[i] and node.forward[i].key < key:
                node = node.forward[i]
            update[i] = node  # last node before the gap at this level
        node = node.forward[0]
        if node and node.key == key:
            return  # no duplicates

        new_level = self._random_level()
        if new_level > self.level:
            for i in range(self.level + 1, new_level + 1):
                update[i] = self.head
            self.level = new_level

        new_node = Node(key, new_level)
        for i in range(new_level + 1):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node

    def contains(self, key: int) -> bool:
        node = self.head
        for i in range(self.level, -1, -1):
            while node.forward[i] and node.forward[i].key < key:
                node = node.forward[i]
        node = node.forward[0]
        return node is not None and node.key == key

    def delete(self, key: int) -> bool:
        update = [self.head] * (self.max_level + 1)
        node = self.head
        for i in range(self.level, -1, -1):
            while node.forward[i] and node.forward[i].key < key:
                node = node.forward[i]
            update[i] = node
        target = node.forward[0]
        if not target or target.key != key:
            return False
        for i in range(self.level + 1):
            if update[i].forward[i] is target:
                update[i].forward[i] = target.forward[i]
        while self.level > 0 and self.head.forward[self.level] is None:
            self.level -= 1
        return True

    def to_list(self) -> list[int]:
        out: list[int] = []
        node = self.head.forward[0]
        while node:
            out.append(node.key)
            node = node.forward[0]
        return out

    def level_sizes(self) -> list[int]:
        sizes: list[int] = []
        for i in range(self.level + 1):
            count = 0
            node = self.head.forward[i]
            while node:
                count += 1
                node = node.forward[i]
            sizes.append(count)
        return sizes


def main() -> None:
    sl = SkipList(seed=7)
    for key in [3, 6, 7, 9, 12, 19, 17, 26, 21, 25]:
        sl.insert(key)

    print(f"sorted contents: {sl.to_list()}")
    print(f"contains 19: {sl.contains(19)}, contains 20: {sl.contains(20)}")
    print(f"level occupancy (bottom to top): {sl.level_sizes()}")
    print("  upper levels hold roughly half of the level below — the express lanes")

    print(f"delete 12 -> {sl.delete(12)}, delete 100 -> {sl.delete(100)}")
    print(f"after deletion: {sl.to_list()}")

    # Stays correct and near-balanced across many operations.
    big = SkipList(seed=1)
    keys = list(range(2000))
    for k in keys:
        big.insert(k)
    print(f"2000 sorted inserts: contents correct = {big.to_list() == keys}")
    print(f"top level in use: {big.level} (~log2(2000) = 11)")


if __name__ == "__main__":
    main()
