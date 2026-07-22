"""Permutations: every ordering of a sequence, generated recursively.

The swap method fixes one position at a time. At depth k, every element from
index k onwards is swapped into position k in turn, and the rest is permuted
recursively; the swap is undone on the way out so the array returns to its
previous state. That undo is what makes the whole thing work in place with no
extra bookkeeping.

Duplicates need care. If the input has repeated values, swapping two equal
elements into the same slot produces the same permutation twice, so at each
depth we remember which values have already been placed there and skip repeats.

There are n! permutations, so any generator is O(n * n!) to enumerate. The
standard library's itertools.permutations is faster and lazy, but it treats
positions as distinct and so does not deduplicate equal values.
"""

from itertools import permutations as it_permutations


def permutations_swap(items: list[int]) -> list[list[int]]:
    result: list[list[int]] = []
    a = list(items)

    def recurse(k: int) -> None:
        if k == len(a):
            result.append(list(a))  # copy: `a` keeps mutating
            return
        for i in range(k, len(a)):
            a[k], a[i] = a[i], a[k]
            recurse(k + 1)
            a[k], a[i] = a[i], a[k]  # undo, restoring the caller's order

    recurse(0)
    return result


def permutations_unique(items: list[int]) -> list[list[int]]:
    result: list[list[int]] = []
    a = list(items)

    def recurse(k: int) -> None:
        if k == len(a):
            result.append(list(a))
            return
        seen: set[int] = set()
        for i in range(k, len(a)):
            if a[i] in seen:  # this value already occupied slot k
                continue
            seen.add(a[i])
            a[k], a[i] = a[i], a[k]
            recurse(k + 1)
            a[k], a[i] = a[i], a[k]
    recurse(0)
    return result


def permutations_build(items: list[int]) -> list[list[int]]:
    """The other classic shape: pick a remaining element, recurse on the rest."""
    if not items:
        return [[]]
    out: list[list[int]] = []
    for i, x in enumerate(items):
        rest = items[:i] + items[i + 1:]
        out.extend([x] + tail for tail in permutations_build(rest))
    return out


def main() -> None:
    print(f"swap  [1,2,3]: {permutations_swap([1, 2, 3])}")
    print(f"build [1,2,3]: {permutations_build([1, 2, 3])}")

    dupes = [1, 1, 2]
    print(f"swap   [1,1,2]: {permutations_swap(dupes)}")
    print(f"unique [1,1,2]: {permutations_unique(dupes)}")

    # The swap version is lexicographically unordered; itertools is ordered by
    # position, which matches sorted input.
    print(f"itertools [1,2,3]: {[list(p) for p in it_permutations([1, 2, 3])]}")
    print(f"itertools [1,1,2]: {[list(p) for p in it_permutations([1, 1, 2])]}")

    print(f"empty: {permutations_swap([])}")
    print(f"single: {permutations_swap([7])}")
    print(f"count for n=5: {len(permutations_swap([1, 2, 3, 4, 5]))}")


if __name__ == "__main__":
    main()
