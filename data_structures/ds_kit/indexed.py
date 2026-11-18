"""Lookup-oriented containers: MinHeap, Trie and LRUCache."""

from collections import OrderedDict
from collections.abc import Hashable
from typing import Any


class MinHeap[T]:
    """Binary min-heap in a list; ``push``/``pop`` are O(log n)."""

    def __init__(self) -> None:
        self._a: list[T] = []

    def push(self, item: T) -> None:
        a = self._a
        a.append(item)
        i = len(a) - 1
        while i and a[i] < a[(i - 1) // 2]:
            a[i], a[(i - 1) // 2] = a[(i - 1) // 2], a[i]
            i = (i - 1) // 2

    def pop(self) -> T:
        a = self._a
        if not a:
            raise IndexError("pop from empty heap")
        top, last = a[0], a.pop()
        if a:
            a[0] = last
            i = 0
            while True:
                small = i
                for child in (2 * i + 1, 2 * i + 2):
                    if child < len(a) and a[child] < a[small]:
                        small = child
                if small == i:
                    break
                a[i], a[small] = a[small], a[i]
                i = small
        return top

    def peek(self) -> T:
        if not self._a:
            raise IndexError("peek at empty heap")
        return self._a[0]

    def __len__(self) -> int:
        return len(self._a)


class Trie:
    """Prefix tree for words: insert, exact lookup and prefix completion."""

    def __init__(self) -> None:
        self._root: dict[str, Any] = {}

    _END = "$"

    def insert(self, word: str) -> None:
        node = self._root
        for ch in word:
            node = node.setdefault(ch, {})
        node[self._END] = True

    def _walk(self, prefix: str) -> dict[str, Any] | None:
        node = self._root
        for ch in prefix:
            if ch not in node:
                return None
            node = node[ch]
        return node

    def __contains__(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and self._END in node

    def with_prefix(self, prefix: str) -> list[str]:
        node = self._walk(prefix)
        out: list[str] = []

        def collect(n: dict[str, Any], acc: str) -> None:
            if self._END in n:
                out.append(acc)
            for ch in sorted(k for k in n if k != self._END):
                collect(n[ch], acc + ch)

        if node is not None:
            collect(node, prefix)
        return out


class LRUCache:
    """Evicts the least recently used key once ``capacity`` is exceeded."""

    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self._data: OrderedDict[Hashable, Any] = OrderedDict()

    def get(self, key: Hashable, default: Any = None) -> Any:
        if key not in self._data:
            return default
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key: Hashable, value: Any) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self.capacity:
            self._data.popitem(last=False)

    def __len__(self) -> int:
        return len(self._data)

    def keys(self) -> list[Hashable]:
        return list(self._data)  # least to most recently used
