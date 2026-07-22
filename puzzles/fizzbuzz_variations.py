"""FizzBuzz, four ways — a small problem that exposes how you structure code.

The naive chain works and is perfectly readable at three rules. The interesting
part is what happens when a fourth rule arrives: the conditional version needs
a new branch in exactly the right position, while the table-driven version
needs one new tuple and no logic change at all.

That is the real lesson — data-driven code moves change out of control flow.
The generator version adds laziness, and the divisibility-free version shows
that counters can replace the modulo entirely.
"""

from collections.abc import Iterator


def fizzbuzz_conditional(n: int) -> str:
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)


RULES = ((3, "Fizz"), (5, "Buzz"))
EXTENDED = ((3, "Fizz"), (5, "Buzz"), (7, "Bazz"))


def fizzbuzz_table(n: int, rules: tuple[tuple[int, str], ...] = RULES) -> str:
    """One rule per tuple: adding a rule needs no new branch."""
    word = "".join(label for divisor, label in rules if n % divisor == 0)
    return word or str(n)


def fizzbuzz_stream(limit: int) -> Iterator[str]:
    """Lazy: works for an unbounded range without building a list."""
    for n in range(1, limit + 1):
        yield fizzbuzz_table(n)


def fizzbuzz_no_modulo(limit: int) -> list[str]:
    """Counters instead of %, the way a hardware implementation would do it."""
    out: list[str] = []
    three = five = 0
    for n in range(1, limit + 1):
        three += 1
        five += 1
        word = ""
        if three == 3:
            word += "Fizz"
            three = 0
        if five == 5:
            word += "Buzz"
            five = 0
        out.append(word or str(n))
    return out


def main() -> None:
    print("conditional:")
    print(f"  {[fizzbuzz_conditional(n) for n in range(1, 16)]}")

    print("table-driven, same answer:")
    table = [fizzbuzz_table(n) for n in range(1, 16)]
    print(f"  matches: {table == [fizzbuzz_conditional(n) for n in range(1, 16)]}")

    print("adding a fourth rule costs one tuple, no new branch:")
    print(f"  {[fizzbuzz_table(n, EXTENDED) for n in (3, 5, 7, 15, 21, 35, 105)]}")

    print("lazy stream:")
    stream = fizzbuzz_stream(1_000_000)
    print(f"  first five without computing the rest: {[next(stream) for _ in range(5)]}")

    print("counter version agrees:")
    print(f"  {fizzbuzz_no_modulo(15) == table}")

    print("edge cases:")
    print(f"  limit 0 -> {fizzbuzz_no_modulo(0)}")
    print(f"  n=1 -> {fizzbuzz_table(1)!r}, n=15 -> {fizzbuzz_table(15)!r}")


if __name__ == "__main__":
    main()
