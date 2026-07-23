"""Persistent segment tree: every update yields a new version, sharing nodes.

A normal update mutates the tree in place, destroying the old state. A
persistent update instead copies only the O(log n) nodes on the path from root
to leaf and reuses the untouched subtrees, so each version costs O(log n) extra
memory and every past version stays queryable forever.

Keeping an array of roots — one per version — turns the structure into a
time machine: query version v to see the array as it was after the v-th update.
The classic application is "k-th smallest value in a range", answered by
subtracting two prefix versions of a frequency tree, which the second half of
this file demonstrates.

Build O(n), update and query O(log n) time and O(log n) new nodes per update.
"""

from dataclasses import dataclass


@dataclass
class Node:
    total: int
    left: "Node | None" = None
    right: "Node | None" = None


def build(lo: int, hi: int) -> Node:
    if lo == hi:
        return Node(0)
    mid = (lo + hi) // 2
    return Node(0, build(lo, mid), build(mid + 1, hi))


def update(node: Node, lo: int, hi: int, index: int, delta: int) -> Node:
    """Return a NEW root reflecting a[index] += delta, sharing untouched nodes."""
    if lo == hi:
        return Node(node.total + delta)
    mid = (lo + hi) // 2
    if index <= mid:
        return Node(node.total + delta, update(node.left, lo, mid, index, delta), node.right)
    return Node(node.total + delta, node.left, update(node.right, mid + 1, hi, index, delta))


def range_sum(node: Node, lo: int, hi: int, ql: int, qr: int) -> int:
    if qr < lo or hi < ql:
        return 0
    if ql <= lo and hi <= qr:
        return node.total
    mid = (lo + hi) // 2
    return (range_sum(node.left, lo, mid, ql, qr)
            + range_sum(node.right, mid + 1, hi, ql, qr))


def kth_smallest(older: Node, newer: Node, lo: int, hi: int, k: int) -> int:
    """k-th smallest (1-indexed) among counts that differ between two versions."""
    if lo == hi:
        return lo
    mid = (lo + hi) // 2
    left_count = newer.left.total - older.left.total
    if k <= left_count:
        return kth_smallest(older.left, newer.left, lo, mid, k)
    return kth_smallest(older.right, newer.right, mid + 1, hi, k - left_count)


def main() -> None:
    n = 8
    versions = [build(0, n - 1)]  # version 0: all zeros

    # Each update forks a new version off the latest.
    for index, delta in [(2, 5), (4, 3), (2, 1), (7, 9)]:
        versions.append(update(versions[-1], 0, n - 1, index, delta))

    print("range_sum[0:8) at each version:")
    for v, root in enumerate(versions):
        print(f"  version {v}: {range_sum(root, 0, n - 1, 0, n - 1)}")

    print(f"version 1 saw only a[2]=5: sum[0:4) = "
          f"{range_sum(versions[1], 0, n - 1, 0, 3)}")
    print(f"version 4 with all updates: sum[0:8) = "
          f"{range_sum(versions[4], 0, n - 1, 0, 7)}")
    print("old versions are untouched — the past is immutable")

    # k-th smallest in a subarray, via prefix versions of a frequency tree.
    values = [1, 5, 2, 6, 3, 7, 4]
    coords = sorted(set(values))
    rank = {v: i for i, v in enumerate(coords)}
    prefix = [build(0, len(coords) - 1)]
    for v in values:
        prefix.append(update(prefix[-1], 0, len(coords) - 1, rank[v], 1))

    def query_kth(lo: int, hi: int, k: int) -> int:
        # counts in [lo, hi) = version(hi) - version(lo)
        idx = kth_smallest(prefix[lo], prefix[hi], 0, len(coords) - 1, k)
        return coords[idx]

    print("k-th smallest in a range (values =", values, "):")
    for lo, hi, k in [(1, 5, 2), (0, 7, 4), (2, 6, 1)]:
        got = query_kth(lo, hi, k)
        expected = sorted(values[lo:hi])[k - 1]
        print(f"  {k}-th smallest of {values[lo:hi]} -> {got} (check {expected})")


if __name__ == "__main__":
    main()
