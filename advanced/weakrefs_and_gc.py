"""Reference counting, cycles, and weak references.

CPython frees an object the moment its refcount hits zero. That handles almost
everything — but not cycles: a list containing itself, or two objects pointing
at each other, keep each other alive. The cyclic garbage collector exists
solely to find and break those.

A *weak* reference lets you point at an object without keeping it alive. It is
the right tool for caches, registries, and back-pointers (child -> parent),
where a strong reference would leak.
"""

import gc
import sys
import weakref


class Node:
    def __init__(self, name: str) -> None:
        self.name = name
        self.other: "Node | None" = None

    def __repr__(self) -> str:
        return f"Node({self.name})"

    def __del__(self) -> None:
        print(f"  {self.name} collected")


class Child:
    def __init__(self, parent: "Parent") -> None:
        self._parent = weakref.ref(parent)  # does not keep the parent alive

    @property
    def parent(self) -> "Parent | None":
        return self._parent()


class Parent:
    def __init__(self) -> None:
        self.children: list[Child] = []

    def add(self) -> Child:
        child = Child(self)
        self.children.append(child)
        return child


def main() -> None:
    obj = Node("plain")
    print(f"refcount: {sys.getrefcount(obj) - 1} (minus the temporary argument)")
    alias = obj  # noqa: F841
    print(f"after aliasing: {sys.getrefcount(obj) - 1}")
    del alias
    del obj  # refcount hits zero here

    print("creating a cycle:")
    a, b = Node("a"), Node("b")
    a.other, b.other = b, a
    del a, b  # refcounts are still 1 each — nothing is freed
    print("  deleted both names, nothing collected yet")
    collected = gc.collect()  # the cyclic collector breaks it
    print(f"  gc.collect() reclaimed {collected} objects")

    print("weak reference:")
    target = Node("target")
    ref = weakref.ref(target)
    print(f"  ref() -> {ref()}")
    del target
    print(f"  after del: ref() -> {ref()}")

    print("WeakValueDictionary drops entries when the value dies:")
    cache: weakref.WeakValueDictionary[str, Node] = weakref.WeakValueDictionary()
    live = Node("cached")
    cache["k"] = live
    print(f"  in cache: {list(cache)}")
    del live
    print(f"  after the last strong reference went away: {list(cache)}")

    parent = Parent()
    child = parent.add()
    print(f"child -> parent: {child.parent is parent} (no reference cycle)")

    print(f"gc thresholds: {gc.get_threshold()}, tracked objects: {len(gc.get_objects()) > 0}")


if __name__ == "__main__":
    main()
