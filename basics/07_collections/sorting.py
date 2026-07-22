"""Sorting — `sorted()`, `.sort()`, and the `key` function.

`sorted(iterable)` returns a new list and works on anything iterable.
`list.sort()` sorts in place and returns None (assigning its result is a
classic bug: you get None, not a sorted list).

Both are Timsort: O(n log n) worst case, and **stable** — records that compare
equal stay in their original relative order. Stability is what makes
multi-pass sorting work: sort by the secondary key first, then the primary.

`key=` is called once per element and its result is compared. Prefer it over
the removed `cmp=`; it is both faster and easier to reason about.
"""

from operator import itemgetter


def main() -> None:
    nums = [5, 2, 9, 1]
    print(f"sorted(nums)  = {sorted(nums)}   original still {nums}")
    print(f"reverse       = {sorted(nums, reverse=True)}")

    result = nums.sort()
    print(f"nums.sort() returns {result!r} and mutates: {nums}")

    words = ["banana", "kiwi", "apple", "fig"]
    print(f"by length     = {sorted(words, key=len)}")
    print(f"case-insensitive = {sorted(['b', 'A', 'c'], key=str.lower)}")

    people = [("Ada", 36), ("Grace", 45), ("Alan", 36)]
    print(f"by age        = {sorted(people, key=itemgetter(1))}")

    # A tuple key sorts by several fields at once; the minus flips one.
    print(f"age desc, name asc = {sorted(people, key=lambda p: (-p[1], p[0]))}")

    # Stability lets you chain sorts: least significant key first.
    by_name = sorted(people, key=itemgetter(0))
    by_age_then_name = sorted(by_name, key=itemgetter(1))
    print(f"stable two-pass = {by_age_then_name}")

    # min/max take the same key argument.
    print(f"longest word = {max(words, key=len)}")

    # Sorting a dict by value.
    scores = {"Ada": 95, "Alan": 83, "Grace": 91}
    print(f"ranked = {sorted(scores.items(), key=itemgetter(1), reverse=True)}")

    # Elements must be mutually comparable.
    try:
        sorted([1, "two"])  # type: ignore[list-item]
    except TypeError as exc:
        print(f"TypeError: {exc}")


if __name__ == "__main__":
    main()
