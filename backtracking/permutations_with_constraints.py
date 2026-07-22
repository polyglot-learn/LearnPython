"""Constrained permutations: prune during the search, do not filter after it.

The task is to produce only the orderings that satisfy some rule. The obvious
approach generates all n! permutations and keeps the ones that pass, which is
correct but does the full factorial amount of work regardless of how strict the
rule is.

Backtracking does better when the rule can be checked on a prefix. If a partial
arrangement already violates the rule, every one of the (n - k)! completions of
that prefix violates it too, so the whole subtree can be abandoned at depth k
instead of at depth n. The saving is multiplicative in the depth at which the
violation appears.

The requirement is that the predicate be prefix-monotone: once a prefix is
invalid, extending it can never repair it. "No two adjacent elements differ by
one" has that property; "the last element is even" does not, and for rules like
that you can only check at the leaves. The code below counts visited nodes both
ways so the difference is visible rather than asserted.
"""

from collections.abc import Callable
from itertools import permutations as it_permutations

Prefix = list[int]


def permutations_filter_late(
    items: list[int], is_valid: Callable[[Prefix], bool]
) -> tuple[list[Prefix], int]:
    """Generate everything, then filter. Returns (results, permutations built)."""
    built = 0
    out: list[Prefix] = []
    for p in it_permutations(items):
        built += 1
        if is_valid(list(p)):
            out.append(list(p))
    return out, built


def permutations_prune_early(
    items: list[int], prefix_ok: Callable[[Prefix], bool]
) -> tuple[list[Prefix], int]:
    """Extend only prefixes that already satisfy the rule. Returns (results, nodes)."""
    out: list[Prefix] = []
    used = [False] * len(items)
    prefix: Prefix = []
    nodes = 0

    def recurse() -> None:
        nonlocal nodes
        if len(prefix) == len(items):
            out.append(list(prefix))
            return
        for i, x in enumerate(items):
            if used[i]:
                continue
            prefix.append(x)
            nodes += 1
            if prefix_ok(prefix):  # dead prefixes are dropped here, not at depth n
                used[i] = True
                recurse()
                used[i] = False
            prefix.pop()

    recurse()
    return out, nodes


def no_adjacent_consecutive(prefix: Prefix) -> bool:
    """Prefix-monotone: adjacent values must never differ by exactly one."""
    return len(prefix) < 2 or abs(prefix[-1] - prefix[-2]) != 1


def no_adjacent_consecutive_full(perm: Prefix) -> bool:
    """The same rule stated over a whole permutation, for the filtering version."""
    return all(abs(a - b) != 1 for a, b in zip(perm, perm[1:]))


def derangement_prefix(prefix: Prefix) -> bool:
    """No element may sit at its own 1-based position."""
    return prefix[-1] != len(prefix)


def main() -> None:
    items = [1, 2, 3, 4, 5]

    late, built = permutations_filter_late(items, no_adjacent_consecutive_full)
    early, nodes = permutations_prune_early(items, no_adjacent_consecutive)
    print(f"no adjacent consecutive values, n={len(items)}")
    print(f"  results: {len(early)}, same set as filtering: {sorted(early) == sorted(late)}")
    print(f"  filter-late built {built} full permutations")
    print(f"  prune-early visited {nodes} partial arrangements")
    print(f"  first few: {early[:4]}")

    derangements, dn = permutations_prune_early(items, derangement_prefix)
    print(f"\nderangements of 1..5: {len(derangements)} (expected 44), "
          f"nodes visited {dn}")
    print(f"  first few: {derangements[:4]}")

    # Edge cases: nothing to permute, and a rule nothing can satisfy.
    print(f"\nempty input: {permutations_prune_early([], no_adjacent_consecutive)}")
    print(f"single item: {permutations_prune_early([7], derangement_prefix)}")
    print(f"impossible rule: {permutations_prune_early(items, lambda p: False)}")

    # The gap widens fast with n: at n=8 the filter builds 40320 permutations.
    for n in (6, 7, 8):
        seq = list(range(1, n + 1))
        _, built_n = permutations_filter_late(seq, no_adjacent_consecutive_full)
        res_n, nodes_n = permutations_prune_early(seq, no_adjacent_consecutive)
        print(f"n={n}: {len(res_n)} results, built={built_n}, pruned nodes={nodes_n}")


if __name__ == "__main__":
    main()
