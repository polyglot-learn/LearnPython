"""Recursion limits, the absence of tail calls, and memoised recursion.

CPython gives every call a real stack frame and caps the number of nested
frames at sys.getrecursionlimit(), about 1000 by default. The cap exists to
turn a runaway recursion into a catchable RecursionError instead of a C-level
stack overflow that would kill the process, so raising it too far trades one
failure for a worse one.

A tail call is a call in the final position of a function, where the caller has
nothing left to do. Languages with tail-call optimisation reuse the frame and
turn such recursion into a loop. Python deliberately does not: keeping every
frame is what makes tracebacks complete and introspection honest. So a tail
recursive factorial still costs O(n) stack in Python, and the only reliable fix
is to write the loop yourself, or to carry your own explicit stack.

Memoisation is the other lever. functools.cache turns exponential branching
recursion, like naive Fibonacci, into linear time by never recomputing a
subproblem — but it does not reduce depth, so a deep chain still needs the
iterative rewrite.
"""

import sys
from functools import cache


def factorial_recursive(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)  # not a tail call: the multiply waits


def factorial_tail(n: int, acc: int = 1) -> int:
    """Tail recursive in form; Python still grows the stack linearly."""
    if n <= 1:
        return acc
    return factorial_tail(n - 1, acc * n)


def factorial_iterative(n: int) -> int:
    acc = 1
    for k in range(2, n + 1):
        acc *= k
    return acc


def fib_naive(n: int) -> int:
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


@cache
def fib_cached(n: int) -> int:
    if n < 2:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)


def sum_to_iterative(n: int) -> int:
    """The iterative rewrite of `sum_to(n) = n + sum_to(n-1)`."""
    total = 0
    while n > 0:
        total += n
        n -= 1
    return total


def with_recursion_limit(limit: int):
    """Temporarily raise the limit, restoring it even on error."""
    class _Ctx:
        def __enter__(self) -> None:
            self.old = sys.getrecursionlimit()
            sys.setrecursionlimit(limit)

        def __exit__(self, *exc: object) -> None:
            sys.setrecursionlimit(self.old)
    return _Ctx()


def main() -> None:
    print(f"default recursion limit: {sys.getrecursionlimit()}")
    print(f"factorial_recursive(10): {factorial_recursive(10)}")
    print(f"factorial_tail(10):      {factorial_tail(10)}")
    print(f"factorial_iterative(10): {factorial_iterative(10)}")

    try:
        factorial_tail(5000)
    except RecursionError:
        print("factorial_tail(5000): RecursionError (no tail-call optimisation)")
    # bit_length avoids CPython's 4300-digit cap on int-to-str conversion.
    print(f"factorial_iterative(5000) is {factorial_iterative(5000).bit_length()} bits")

    # Raising the limit works, but each frame is real memory; keep it modest.
    with with_recursion_limit(20_000):
        print(f"raised limit: {sys.getrecursionlimit()}, factorial_tail(5000) is "
              f"{factorial_tail(5000).bit_length()} bits")
    print(f"restored limit: {sys.getrecursionlimit()}")

    print(f"fib_naive(25):  {fib_naive(25)}")
    print(f"fib_cached(25): {fib_cached(25)}")
    print(f"fib_cached(300): {fib_cached(300)}")
    print(f"cache stats: {fib_cached.cache_info()}")

    print(f"sum_to_iterative(1_000_000): {sum_to_iterative(1_000_000)}")


if __name__ == "__main__":
    main()
