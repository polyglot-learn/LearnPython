"""Examples and self-check: python3 -m dynamic_programming.dp_kit"""

import itertools
import sys

from . import coin_change, count_paths, edit_distance, knapsack, lcs, lis, memoize


def examples() -> None:
    print("1. knapsack:", knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7))
    print("2. LCS:", repr(lcs("AGGTAB", "GXTXAYB")))
    print("3. edit distance:", edit_distance("kitten", "sitting"), edit_distance("", "abc"))
    print("4. coins for 63:", coin_change([1, 5, 10, 25], 63), "| for 3 with [2]:", coin_change([2], 3))
    print("5. LIS:", lis([10, 9, 2, 5, 3, 7, 101, 18]))
    print("6. grid paths 3x3:", count_paths(3, 3), "| with a wall:", count_paths(3, 3, {(1, 1)}))

    @memoize
    def fib(n: int) -> int:
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    print("7. memoized fib(60) =", fib(60), "in", fib.calls, "calls (naive needs ~5e12)")


def self_check() -> None:
    weights, values, cap = [2, 3, 4, 5], [3, 4, 5, 6], 8
    best = max(
        sum(values[i] for i in combo)
        for r in range(len(weights) + 1)
        for combo in itertools.combinations(range(len(weights)), r)
        if sum(weights[i] for i in combo) <= cap
    )
    value, chosen = knapsack(weights, values, cap)
    assert value == best == sum(values[i] for i in chosen)
    assert sum(weights[i] for i in chosen) <= cap
    assert len(lcs("ABCBDAB", "BDCABA")) == 4
    assert edit_distance("flaw", "lawn") == 2
    assert coin_change([2], 3) is None and sum(coin_change([1, 5, 10, 25], 63)) == 63
    result = lis([3, 1, 4, 1, 5, 9, 2, 6])
    assert result == sorted(set(result)) and len(result) == 4
    assert count_paths(3, 3) == 6 and lis([]) == []


def main() -> int:
    examples()
    self_check()
    print("self-check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
