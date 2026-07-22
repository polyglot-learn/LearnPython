"""LRU cache: a hash map plus a doubly linked list, both operations O(1).

The map gives O(1) lookup; the list gives O(1) reordering. On a hit, move the
node to the front; on an insert past capacity, evict the tail. Neither
structure alone can do both — that pairing *is* the algorithm.

Python's `OrderedDict.move_to_end` is exactly this, in C, and
`functools.lru_cache` wraps it as a decorator.
"""

from collections import OrderedDict


class Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: int = 0, value: int = 0) -> None:
        self.key, self.value = key, value
        self.prev: "Node | None" = None
        self.next: "Node | None" = None


class LRUCache:
    """Hand-built version: sentinel head/tail nodes remove all edge cases."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.map: dict[int, Node] = {}
        self.head, self.tail = Node(), Node()  # sentinels
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node: Node) -> None:
        node.prev.next, node.next.prev = node.next, node.prev

    def _push_front(self, node: Node) -> None:
        node.next, node.prev = self.head.next, self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int | None:
        node = self.map.get(key)
        if node is None:
            return None
        self._remove(node)
        self._push_front(node)  # most recently used
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            self._remove(self.map[key])
        node = Node(key, value)
        self.map[key] = node
        self._push_front(node)
        if len(self.map) > self.capacity:
            oldest = self.tail.prev
            self._remove(oldest)
            del self.map[oldest.key]

    def keys_mru_first(self) -> list[int]:
        out, node = [], self.head.next
        while node is not self.tail:
            out.append(node.key)
            node = node.next
        return out


class LRUCacheOrdered:
    """The same semantics in a dozen lines, using OrderedDict."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.store: OrderedDict[int, int] = OrderedDict()

    def get(self, key: int) -> int | None:
        if key not in self.store:
            return None
        self.store.move_to_end(key, last=False)
        return self.store[key]

    def put(self, key: int, value: int) -> None:
        self.store[key] = value
        self.store.move_to_end(key, last=False)
        if len(self.store) > self.capacity:
            self.store.popitem(last=True)


def main() -> None:
    cache = LRUCache(2)
    cache.put(1, 100)
    cache.put(2, 200)
    print(f"get(1) = {cache.get(1)}   order: {cache.keys_mru_first()}")
    cache.put(3, 300)  # evicts key 2, the least recently used
    print(f"get(2) = {cache.get(2)}  (evicted)")
    print(f"order: {cache.keys_mru_first()}")

    ordered = LRUCacheOrdered(2)
    ordered.put(1, 1)
    ordered.put(2, 2)
    ordered.get(1)
    ordered.put(3, 3)
    print(f"OrderedDict version keeps: {list(ordered.store)}")

    from functools import lru_cache

    @lru_cache(maxsize=2)
    def square(n: int) -> int:
        return n * n

    for n in (2, 3, 2, 4, 3):
        square(n)
    print(f"functools.lru_cache: {square.cache_info()}")


if __name__ == "__main__":
    main()
