"""Examples and self-check: python3 -m data_structures.ds_kit"""

import random
import sys

from . import LinkedList, LRUCache, MinHeap, Queue, Stack, Trie


def balanced(text: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: Stack[str] = Stack()
    for ch in text:
        if ch in "([{":
            stack.push(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


def examples() -> None:
    print("1. stack, balanced brackets:", balanced("{[()]}"), balanced("([)]"))
    q = Queue([1, 2, 3])
    q.enqueue(4)
    before = str(q)
    print("2. queue:", before, "-> dequeue", q.dequeue(), "->", q)
    ll = LinkedList([1, 2, 3])
    ll.append(4)
    ll.reverse()
    print("3. linked list reversed:", ll, "| len", len(ll))
    h: MinHeap[int] = MinHeap()
    for n in [5, 1, 4, 2, 3]:
        h.push(n)
    print("4. heap drains in order:", [h.pop() for _ in range(len(h))])
    t = Trie()
    for w in ["car", "card", "care", "cat", "dog"]:
        t.insert(w)
    print("5. trie 'car' in:", "car" in t, "| 'ca' in:", "ca" in t, "| prefix 'car':", t.with_prefix("car"))
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")
    c.put("c", 3)
    print("6. LRU keys after touching a then adding c:", c.keys(), "| b ->", c.get("b"))


def self_check() -> None:
    rng = random.Random(5)
    nums = [rng.randint(0, 99) for _ in range(200)]
    h: MinHeap[int] = MinHeap()
    for n in nums:
        h.push(n)
    assert [h.pop() for _ in nums] == sorted(nums)
    ll = LinkedList(nums[:10])
    assert list(ll) == nums[:10] and ll.remove(nums[3]) and len(ll) == 9
    assert not ll.remove(1000)
    for cls, add, take in ((Stack, "push", "pop"), (Queue, "enqueue", "dequeue")):
        empty = cls()
        try:
            getattr(empty, take)()
        except IndexError:
            pass
        else:
            raise AssertionError(f"{cls.__name__} popped from empty")
    try:
        LRUCache(0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero capacity accepted")


def main() -> int:
    examples()
    self_check()
    print("self-check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
