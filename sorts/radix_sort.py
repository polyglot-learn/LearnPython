"""Radix sort: counting-sort the numbers one digit at a time, least significant first.

LSD radix sort works only because the per-digit sort is *stable* — each pass
preserves the ordering established by the previous, less significant digits.

Complexity: O(d * (n + b)) for d digits in base b. With a fixed word size that
is O(n), beating the comparison lower bound because it never compares two keys
to each other.
"""


def radix_sort(values: list[int], base: int = 10) -> list[int]:
    if not values:
        return []
    negatives = [-v for v in values if v < 0]
    positives = [v for v in values if v >= 0]
    sorted_pos = _radix_nonneg(positives, base)
    sorted_neg = [-v for v in reversed(_radix_nonneg(negatives, base))]
    return sorted_neg + sorted_pos


def _radix_nonneg(values: list[int], base: int) -> list[int]:
    if not values:
        return []
    a = list(values)
    exponent = 1
    largest = max(a)
    while largest // exponent > 0:
        a = _counting_pass(a, exponent, base)
        exponent *= base
    return a


def _counting_pass(values: list[int], exponent: int, base: int) -> list[int]:
    counts = [0] * base
    for v in values:
        counts[(v // exponent) % base] += 1
    for i in range(1, base):
        counts[i] += counts[i - 1]
    out = [0] * len(values)
    for v in reversed(values):  # stability is essential here
        digit = (v // exponent) % base
        counts[digit] -= 1
        out[counts[digit]] = v
    return out


def main() -> None:
    print(radix_sort([170, 45, 75, 90, 802, 24, 2, 66]))
    print(radix_sort([-5, 3, -1, 0, 2]))
    print(radix_sort([170, 45, 75], base=2))
    print(radix_sort([]))


if __name__ == "__main__":
    main()
