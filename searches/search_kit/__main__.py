"""Examples and self-check: python3 -m searches.search_kit"""

import random
import sys

from . import ALGORITHMS, contains, find


def examples() -> None:
    nums = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    print("1. every algorithm finds 13 at index", {n: find(nums, 13, n) for n in ALGORITHMS})
    print("2. missing value gives -1:", find(nums, 4))
    words = ["fig", "kiwi", "apple", "mango"]  # sorted by length: 3, 4, 5, 5
    print("3. sorted by length with key=len:", find(words, 4, key=len))
    print("4. duplicates return the leftmost:", find([1, 2, 2, 2, 3], 2))
    print("5. unsorted data needs linear:", find([9, 4, 7, 1], 7, algo="linear"))
    print("6. contains():", contains(nums, 23), contains(nums, 24))


def self_check() -> None:
    rng = random.Random(3)
    for _ in range(300):
        data = sorted(rng.randint(0, 60) for _ in range(rng.randint(0, 40)))
        for target in range(-2, 64):
            expected = data.index(target) if target in data else -1
            for name in ALGORITHMS:
                got = find(data, target, name)
                assert got == expected, (name, data, target, got, expected)


def main() -> int:
    examples()
    self_check()
    print("self-check passed for:", ", ".join(ALGORITHMS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
