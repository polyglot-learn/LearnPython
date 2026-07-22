"""Fenwick tree (binary indexed tree): prefix sums with O(log n) updates.

Half the memory and much simpler code than a segment tree, at the cost of only
supporting *invertible* operations (sums, not minima).

The trick is `i & -i`, which isolates the lowest set bit. Index i covers a
range of exactly that length, so walking `i -= i & -i` visits the O(log n)
nodes that tile a prefix, and `i += i & -i` visits the nodes to update.
"""


class FenwickTree:
    def __init__(self, size: int) -> None:
        self.n = size
        self.tree = [0] * (size + 1)  # 1-indexed internally

    @classmethod
    def from_values(cls, values: list[int]) -> "FenwickTree":
        ft = cls(len(values))
        for i, v in enumerate(values):
            ft.add(i, v)
        return ft

    def add(self, index: int, delta: int) -> None:
        i = index + 1
        while i <= self.n:
            self.tree[i] += delta
            i += i & -i  # move to the next node covering this index

    def prefix_sum(self, count: int) -> int:
        """Sum of the first `count` elements."""
        i, total = count, 0
        while i > 0:
            total += self.tree[i]
            i -= i & -i  # strip the lowest set bit
        return total

    def range_sum(self, lo: int, hi: int) -> int:
        """Sum over [lo, hi) — subtraction is why min() cannot work here."""
        return self.prefix_sum(hi) - self.prefix_sum(lo)

    def find_kth(self, k: int) -> int:
        """Smallest index whose prefix sum is >= k, in O(log n) by bit descent."""
        pos, remaining = 0, k
        step = 1 << (self.n.bit_length())
        while step:
            if pos + step <= self.n and self.tree[pos + step] < remaining:
                pos += step
                remaining -= self.tree[pos]
            step >>= 1
        return pos  # 0-based index of the k-th element


def main() -> None:
    values = [3, 2, -1, 6, 5, 4, -3, 3]
    ft = FenwickTree.from_values(values)
    print(f"values          = {values}")
    print(f"prefix_sum(5)   = {ft.prefix_sum(5)}  (check {sum(values[:5])})")
    print(f"range_sum(2, 6) = {ft.range_sum(2, 6)}  (check {sum(values[2:6])})")

    ft.add(3, 10)  # values[3] += 10
    values[3] += 10
    print(f"after add(3, 10): range_sum(2, 6) = {ft.range_sum(2, 6)} "
          f"(check {sum(values[2:6])})")

    # The bit trick, made visible.
    print("lowest set bit i & -i:")
    for i in (1, 2, 3, 4, 6, 8, 12):
        print(f"  {i:2d} = {i:04b}  ->  {i & -i}")

    counts = FenwickTree.from_values([1, 1, 1, 1, 1, 1])
    print(f"index of the 4th present element: {counts.find_kth(4)}")


if __name__ == "__main__":
    main()
