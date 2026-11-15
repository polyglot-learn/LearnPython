"""Linear containers: Stack, Queue and a singly LinkedList."""

from collections import deque
from collections.abc import Iterable, Iterator
from typing import Any


class Stack[T]:
    """Last in, first out."""

    def __init__(self, items: Iterable[T] = ()) -> None:
        self._items: list[T] = list(items)

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return reversed(self._items)  # top first

    def __repr__(self) -> str:
        return f"Stack({self._items})"


class Queue[T]:
    """First in, first out, backed by a deque so both ends are O(1)."""

    def __init__(self, items: Iterable[T] = ()) -> None:
        self._items: deque[T] = deque(items)

    def enqueue(self, item: T) -> None:
        self._items.append(item)

    def dequeue(self) -> T:
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __repr__(self) -> str:
        return f"Queue({list(self._items)})"


class _Node:
    __slots__ = ("value", "next")

    def __init__(self, value: Any, next: "_Node | None" = None) -> None:
        self.value, self.next = value, next


class LinkedList[T]:
    """Singly linked list with O(1) prepend and O(n) everything else."""

    def __init__(self, items: Iterable[T] = ()) -> None:
        self._head: _Node | None = None
        self._size = 0
        for item in reversed(list(items)):
            self.prepend(item)

    def prepend(self, value: T) -> None:
        self._head = _Node(value, self._head)
        self._size += 1

    def append(self, value: T) -> None:
        node = _Node(value)
        if self._head is None:
            self._head = node
        else:
            cur = self._head
            while cur.next:
                cur = cur.next
            cur.next = node
        self._size += 1

    def remove(self, value: T) -> bool:
        prev, cur = None, self._head
        while cur:
            if cur.value == value:
                if prev:
                    prev.next = cur.next
                else:
                    self._head = cur.next
                self._size -= 1
                return True
            prev, cur = cur, cur.next
        return False

    def reverse(self) -> None:
        prev, cur = None, self._head
        while cur:
            cur.next, prev, cur = prev, cur, cur.next
        self._head = prev

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        cur = self._head
        while cur:
            yield cur.value
            cur = cur.next

    def __repr__(self) -> str:
        return " -> ".join(map(str, self)) or "(empty)"
