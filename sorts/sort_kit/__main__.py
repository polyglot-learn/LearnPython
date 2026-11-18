"""Demo, self-check and tiny benchmark: python3 -m sorts.sort_kit"""

import random
import sys
import time

from . import ALGORITHMS, is_sorted, sort


def self_check() -> None:
    rng = random.Random(7)
    cases = [[], [1], [2, 1], [5, 5, 5], list(range(20)), list(range(20))[::-1]]
    cases += [[rng.randint(-50, 50) for _ in range(rng.randint(2, 80))] for _ in range(50)]
    for name in ALGORITHMS:
        for case in cases:
            for reverse in (False, True):
                expected = sorted(case, reverse=reverse)
                assert sort(case, name, reverse=reverse) == expected, (name, case, reverse)
    # Stability: sort pairs by first element only.
    pairs = [(rng.randint(0, 3), i) for i in range(60)]
    for name in ("insertion", "merge", "heap", "counting", "builtin"):
        got = sort(pairs, name, key=lambda p: p[0])
        assert got == sorted(pairs, key=lambda p: p[0]), f"{name} not stable"
        rev = sort(pairs, name, key=lambda p: p[0], reverse=True)
        assert rev == sorted(pairs, key=lambda p: p[0], reverse=True), f"{name} reverse"
    assert is_sorted([1, 2, 2, 3]) and not is_sorted([2, 1])


def benchmark(n: int = 2000) -> None:
    rng = random.Random(1)
    data = [rng.randint(0, 10_000) for _ in range(n)]
    print(f"sorting {n} random ints:")
    for name in ALGORITHMS:
        start = time.perf_counter()
        sort(data, name)
        print(f"  {name:<10} {(time.perf_counter() - start) * 1000:8.2f} ms")


def main() -> int:
    print(sort([5, 2, 9, 1], algo="merge"))
    print(sort(["pear", "fig", "banana"], key=len, reverse=True))
    self_check()
    print("self-check passed for:", ", ".join(ALGORITHMS))
    benchmark()
    return 0


if __name__ == "__main__":
    sys.exit(main())
