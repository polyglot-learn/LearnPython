"""Fibonacci four ways: the standard tour of what dynamic programming buys you.

The recurrence is fib(n) = fib(n-1) + fib(n-2) with fib(0) = 0, fib(1) = 1.
Written as plain recursion it re-solves the same subproblems over and over and
costs O(phi**n) time — fib(35) already means about 30 million calls.

The key insight is that there are only n distinct subproblems, so each one
should be computed once. Memoisation caches results top-down; the bottom-up
table fills the same values in index order and drops the recursion entirely.
Once you notice that row i only ever reads rows i-1 and i-2, the table
collapses to two variables.

Complexity: naive O(phi**n) time; memoised and bottom-up O(n) time and O(n)
space; the rolling version is O(n) time and O(1) space.
"""

from time import perf_counter


def fib_naive(n: int) -> int:
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_memo(n: int, cache: dict[int, int] | None = None) -> int:
    if cache is None:
        cache = {}
    if n < 2:
        return n
    if n not in cache:
        cache[n] = fib_memo(n - 1, cache) + fib_memo(n - 2, cache)
    return cache[n]


def fib_bottom_up(n: int) -> int:
    if n < 2:
        return n
    table = [0] * (n + 1)
    table[1] = 1
    for i in range(2, n + 1):
        table[i] = table[i - 1] + table[i - 2]
    return table[n]


def fib_rolling(n: int) -> int:
    """Same recurrence, but only the last two values are ever needed."""
    prev, curr = 0, 1
    for _ in range(n):
        prev, curr = curr, prev + curr
    return prev


def timed(label: str, fn, n: int) -> None:
    start = perf_counter()
    value = fn(n)
    elapsed = perf_counter() - start
    print(f"  {label:<12} fib({n}) = {value:<12} in {elapsed * 1000:8.3f} ms")


def main() -> None:
    print("first fifteen:", [fib_rolling(i) for i in range(15)])

    # Edge cases: the recurrence must terminate at the two base cases.
    print("fib(0):", fib_rolling(0), "fib(1):", fib_rolling(1))

    for n in (0, 1, 10, 40):
        assert fib_memo(n) == fib_bottom_up(n) == fib_rolling(n)
    print("all four agree on the values they can each reach")

    print("\ntimed comparison (n = 28, small enough for the naive version):")
    timed("naive", fib_naive, 28)
    timed("memoised", fib_memo, 28)
    timed("bottom-up", fib_bottom_up, 28)
    timed("rolling", fib_rolling, 28)

    print("\nonly the linear versions survive a large n:")
    timed("memoised", fib_memo, 300)
    timed("bottom-up", fib_bottom_up, 300)
    timed("rolling", fib_rolling, 300)


if __name__ == "__main__":
    main()
