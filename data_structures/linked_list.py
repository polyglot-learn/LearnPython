"""Singly linked list: nodes holding a value and a next pointer.

The trade against a Python list: O(1) insert/delete at a known node, but O(n)
indexing and terrible cache locality. In real Python code a list or deque wins
almost always — this is here for the pointer manipulation, which shows up in
interviews and in every lower-level language.

Reversal in place is the classic exercise: three pointers, one pass, O(1) space.
"""

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass
class Node:
    value: int
    next: "Node | None" = None


class LinkedList:
    def __init__(self, values: list[int] | None = None) -> None:
        self.head: Node | None = None
        self.size = 0
        for value in reversed(values or []):
            self.push_front(value)

    def push_front(self, value: int) -> None:
        self.head = Node(value, self.head)
        self.size += 1

    def pop_front(self) -> int:
        if self.head is None:
            raise IndexError("pop from empty list")
        node = self.head
        self.head = node.next
        self.size -= 1
        return node.value

    def find(self, value: int) -> Node | None:
        node = self.head
        while node and node.value != value:
            node = node.next
        return node

    def remove(self, value: int) -> bool:
        prev, node = None, self.head
        while node:
            if node.value == value:
                if prev is None:
                    self.head = node.next
                else:
                    prev.next = node.next
                self.size -= 1
                return True
            prev, node = node, node.next
        return False

    def reverse(self) -> None:
        prev, node = None, self.head
        while node:
            node.next, prev, node = prev, node, node.next
        self.head = prev

    def middle(self) -> int | None:
        """Tortoise and hare: one pass, no length needed."""
        slow = fast = self.head
        while fast and fast.next:
            slow, fast = slow.next, fast.next.next
        return slow.value if slow else None

    def __iter__(self) -> Iterator[int]:
        node = self.head
        while node:
            yield node.value
            node = node.next

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return " -> ".join(str(v) for v in self) or "(empty)"


def main() -> None:
    ll = LinkedList([1, 2, 3, 4, 5])
    print(f"list:    {ll}  (len {len(ll)})")
    print(f"middle:  {ll.middle()}")
    ll.reverse()
    print(f"reversed:{ll}")
    ll.push_front(9)
    print(f"pushed:  {ll}, popped {ll.pop_front()}")
    print(f"remove 3 -> {ll.remove(3)}, now {ll}")
    print(f"remove 99 -> {ll.remove(99)}")
    print(f"find 4 -> {ll.find(4)}")
    print(f"empty: {LinkedList()}")


if __name__ == "__main__":
    main()
