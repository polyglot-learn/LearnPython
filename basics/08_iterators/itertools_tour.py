"""`itertools` — the standard library's iterator toolkit.

Every function here returns a lazy iterator, so they compose into pipelines
that never materialise the intermediate results. Three families:

  infinite   : count, cycle, repeat        (always bound them with islice/takewhile)
  terminating: chain, islice, takewhile, dropwhile, groupby, accumulate, pairwise
  combinatoric: product, permutations, combinations
"""

import itertools as it


def main() -> None:
    print(f"count(10, 2)  -> {list(it.islice(it.count(10, 2), 5))}")
    print(f"cycle('ab')   -> {list(it.islice(it.cycle('ab'), 5))}")
    print(f"repeat(7, 3)  -> {list(it.repeat(7, 3))}")

    print(f"chain         -> {list(it.chain([1, 2], 'ab', (3,)))}")
    print(f"islice(2, 6)  -> {list(it.islice(range(10), 2, 6))}")
    print(f"takewhile <5  -> {list(it.takewhile(lambda n: n < 5, [1, 3, 7, 2]))}")
    print(f"dropwhile <5  -> {list(it.dropwhile(lambda n: n < 5, [1, 3, 7, 2]))}")
    print(f"accumulate    -> {list(it.accumulate([1, 2, 3, 4]))}   (running sums)")
    print(f"accumulate max-> {list(it.accumulate([3, 1, 4, 1, 5], max))}")
    print(f"pairwise      -> {list(it.pairwise([1, 2, 3, 4]))}")
    print(f"batched(3)    -> {list(it.batched(range(7), 3))}")

    # groupby groups *consecutive* equal keys — sort first if you want
    # global grouping. This trips people up constantly.
    words = ["apple", "avocado", "banana", "apricot"]
    print("groupby unsorted:")
    for key, group in it.groupby(words, key=lambda w: w[0]):
        print(f"  {key}: {list(group)}")
    print("groupby after sorting:")
    for key, group in it.groupby(sorted(words), key=lambda w: w[0]):
        print(f"  {key}: {list(group)}")

    print(f"product       -> {list(it.product('ab', [1, 2]))}")
    print(f"permutations  -> {list(it.permutations('abc', 2))}")
    print(f"combinations  -> {list(it.combinations('abcd', 2))}")
    print(f"combos w/ rep -> {list(it.combinations_with_replacement('ab', 2))}")

    # A pipeline: everything stays lazy until the final sum.
    squares = (n * n for n in it.count(1))
    under_1000 = it.takewhile(lambda s: s < 1000, squares)
    print(f"sum of squares under 1000 = {sum(under_1000)}")

    # tee duplicates an iterator when you need two independent passes.
    a, b = it.tee(iter([1, 2, 3]))
    print(f"tee -> {list(a)} and {list(b)}")


if __name__ == "__main__":
    main()
