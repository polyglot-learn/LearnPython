"""Linear search: check every element until you find the target.

The only search that works on unsorted data, and the only one worth using for
a handful of elements — its constant factor is tiny and it touches memory
sequentially.

Complexity: O(n) worst and average, O(1) best, O(1) space.
"""


def linear_search(values: list[int], target: int) -> int:
    """Return the index of `target`, or -1 if absent."""
    for i, value in enumerate(values):
        if value == target:
            return i
    return -1


def linear_search_sentinel(values: list[int], target: int) -> int:
    """Append the target so the loop needs one test per step instead of two."""
    a = list(values)
    a.append(target)
    i = 0
    while a[i] != target:
        i += 1
    return i if i < len(values) else -1


def find_all(values: list[int], target: int) -> list[int]:
    return [i for i, v in enumerate(values) if v == target]


def main() -> None:
    data = [4, 2, 7, 2, 9]
    print(f"linear_search(7) = {linear_search(data, 7)}")
    print(f"linear_search(5) = {linear_search(data, 5)}")
    print(f"sentinel(9) = {linear_search_sentinel(data, 9)}")
    print(f"find_all(2) = {find_all(data, 2)}")
    # The built-ins do the same thing, in C.
    print(f"data.index(7) = {data.index(7)}, 5 in data -> {5 in data}")


if __name__ == "__main__":
    main()
