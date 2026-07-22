"""Project Euler 1: sum of all multiples of 3 or 5 below 1000.

The brute-force loop is O(n) and answers this instantly. The point of the
problem is the closed form: the multiples of k below n sum to
k * m * (m + 1) / 2 where m = (n - 1) // k, so inclusion-exclusion gives
sum(3) + sum(5) - sum(15) in O(1) — and that version still answers instantly
for n = 10^18, where the loop would never finish.

Answer for n = 1000: 233168.
"""


def brute_force(limit: int) -> int:
    return sum(n for n in range(limit) if n % 3 == 0 or n % 5 == 0)


def sum_multiples(k: int, limit: int) -> int:
    """Sum of k, 2k, 3k... below `limit`, in constant time."""
    m = (limit - 1) // k
    return k * m * (m + 1) // 2


def closed_form(limit: int) -> int:
    # Multiples of 15 are counted by both terms, so subtract them once.
    return sum_multiples(3, limit) + sum_multiples(5, limit) - sum_multiples(15, limit)


def main() -> None:
    print(f"brute force below 1000: {brute_force(1000)}")
    print(f"closed form below 1000: {closed_form(1000)}")
    print(f"agree for every limit up to 2000: "
          f"{all(brute_force(n) == closed_form(n) for n in range(2000))}")

    print(f"below 10: {closed_form(10)} (3 + 5 + 6 + 9)")
    print(f"below 1: {closed_form(1)}")
    print(f"below 10**18: {closed_form(10**18)}")
    print("the loop cannot reach that; the formula is O(1)")


if __name__ == "__main__":
    main()
