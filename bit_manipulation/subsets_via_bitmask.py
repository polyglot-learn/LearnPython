"""Subsets as integers: a bitmask is a subset, and counting enumerates them.

For a list of n elements, an n-bit integer describes a subset: bit i set means
element i is in. Counting from 0 to 2^n - 1 therefore walks every subset exactly
once, with no recursion and no bookkeeping. Testing membership is mask >> i & 1
and adding an element is mask | (1 << i), so set operations become single
instructions: union is |, intersection is &, difference is & ~, and the size is
mask.bit_count().

The second idea is submask enumeration. Given a mask, its submasks are the
integers whose set bits are a subset of the mask's. The idiom sub = (sub - 1) &
mask starts at the mask and walks down: subtracting one borrows through the
zeros, and the and immediately discards any bit that is not in the mask, so each
step lands on the next-largest submask. The loop needs the zero submask handled
outside it, because (0 - 1) & mask wraps back to the mask.

Enumerating all subsets is O(2^n). Enumerating all submasks of all masks is
O(3^n), not O(4^n), because each element is in the submask, in the mask only, or
in neither — that bound is what makes subset-sum dynamic programming over masks
practical.
"""


def subsets(items: list[str]) -> list[list[str]]:
    n = len(items)
    return [
        [items[i] for i in range(n) if mask >> i & 1]
        for mask in range(1 << n)
    ]


def subsets_of_size(items: list[str], k: int) -> list[list[str]]:
    n = len(items)
    return [
        [items[i] for i in range(n) if mask >> i & 1]
        for mask in range(1 << n)
        if mask.bit_count() == k
    ]


def submasks(mask: int) -> list[int]:
    """All submasks of `mask`, from largest down to zero."""
    out = []
    sub = mask
    while sub:
        out.append(sub)
        sub = (sub - 1) & mask  # next-largest submask
    out.append(0)  # the loop cannot reach zero without wrapping
    return out


def render(mask: int, width: int) -> str:
    return format(mask, f"0{width}b")


def to_mask(items: list[str], subset: set[str]) -> int:
    return sum(1 << i for i, x in enumerate(items) if x in subset)


def main() -> None:
    items = ["a", "b", "c"]
    print(f"all subsets of {items}:")
    for mask in range(1 << len(items)):
        chosen = [items[i] for i in range(len(items)) if mask >> i & 1]
        print(f"  mask {render(mask, 3)} (={mask}) -> {chosen}")

    print(f"\ncount for n=3: {len(subsets(items))}")
    print(f"count for n=10: {len(subsets(['x'] * 10))}")
    print(f"empty input: {subsets([])}")
    print(f"size-2 subsets: {subsets_of_size(list('abcd'), 2)}")

    m = 0b1011
    subs = submasks(m)
    print(f"\nsubmasks of {render(m, 4)}: "
          f"{[render(s, 4) for s in subs]}")
    print(f"count: {len(subs)}, expected 2^popcount = {1 << m.bit_count()}")
    print(f"all are submasks: {all(s & m == s for s in subs)}")
    print(f"submasks of 0: {submasks(0)}")
    print(f"submasks of 0b1111: {len(submasks(0b1111))}")

    # Set algebra on masks.
    a = to_mask(items, {"a", "b"})
    b = to_mask(items, {"b", "c"})
    full = (1 << len(items)) - 1
    print(f"\na={render(a, 3)} b={render(b, 3)}")
    print(f"union       {render(a | b, 3)}")
    print(f"intersect   {render(a & b, 3)}")
    print(f"difference  {render(a & ~b & full, 3)}")
    print(f"symmetric   {render(a ^ b, 3)}")
    print(f"complement  {render(a ^ full, 3)}")
    print(f"|a| = {a.bit_count()}, a subset of full: {a & full == a}")

    # The 3^n bound, verified by counting.
    for n in (1, 2, 3, 4, 8):
        total = sum(len(submasks(mask)) for mask in range(1 << n))
        print(f"n={n}: submasks over all masks = {total}, 3^n = {3 ** n}")


if __name__ == "__main__":
    main()
