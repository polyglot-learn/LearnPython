"""Boyer-Moore majority vote: the >n/2 element in O(n) time and O(1) space.

Keep a candidate and a counter. A matching element increments it, any other
decrements it, and a zero counter adopts the next element as the new
candidate. Intuition: pair each occurrence of the majority element with a
different element and cancel them; a strict majority always has leftovers.

The algorithm only *finds* a candidate — it does not verify one exists, so a
second pass is required unless a majority is guaranteed.
"""

from collections import Counter


def majority_element(values: list[int]) -> int | None:
    candidate, count = None, 0
    for value in values:
        if count == 0:
            candidate = value
        count += 1 if value == candidate else -1
    # Verify: without this, [1, 2, 3] returns 3.
    if candidate is not None and values.count(candidate) > len(values) // 2:
        return candidate
    return None


def majority_elements_third(values: list[int]) -> list[int]:
    """The >n/3 generalisation: at most two such elements, so track two slots."""
    c1 = c2 = None
    n1 = n2 = 0
    for v in values:
        if v == c1:
            n1 += 1
        elif v == c2:
            n2 += 1
        elif n1 == 0:
            c1, n1 = v, 1
        elif n2 == 0:
            c2, n2 = v, 1
        else:
            n1 -= 1
            n2 -= 1
    return [c for c in (c1, c2) if c is not None and values.count(c) > len(values) // 3]


def main() -> None:
    print(majority_element([2, 2, 1, 1, 1, 2, 2]))
    print(majority_element([1, 2, 3]))
    print(majority_elements_third([1, 1, 1, 3, 3, 2, 2, 2]))
    # The obvious O(n) space alternative.
    print(Counter([2, 2, 1, 1, 1, 2, 2]).most_common(1))


if __name__ == "__main__":
    main()
