"""`break`, `continue`, and the loop `else` clause almost nobody knows.

`break` leaves the loop immediately. `continue` skips to the next iteration.
Both apply to the innermost loop only — Python has no labelled break.

The surprise: a loop can have an `else` block. It runs when the loop finished
*without* hitting `break`. Read it as "no break" rather than "otherwise", and
the search-loop pattern below stops looking strange.
"""


def first_prime_factor(n: int) -> int | None:
    for d in range(2, int(n**0.5) + 1):
        if n % d == 0:
            return d
    return None


def main() -> None:
    # break: stop at the first match.
    for n in [4, 9, 13, 20]:
        if n > 10:
            print(f"first value over 10: {n}")
            break

    # continue: skip the ones you do not care about.
    for n in range(1, 11):
        if n % 3 != 0:
            continue
        print(f"multiple of 3: {n}")

    # for/else: the else runs only if no break happened.
    haystack = [3, 5, 7, 11]
    for x in haystack:
        if x % 2 == 0:
            print(f"found an even number: {x}")
            break
    else:
        print("no even number in the list")  # this runs

    # The same pattern as a primality test.
    for candidate in (91, 97):
        for d in range(2, int(candidate**0.5) + 1):
            if candidate % d == 0:
                print(f"{candidate} is composite ({d} divides it)")
                break
        else:
            print(f"{candidate} is prime")

    # while/else works the same way.
    n = 3
    while n > 0:
        n -= 1
    else:
        print("while finished without break")

    print(f"first_prime_factor(91) = {first_prime_factor(91)}")

    # No labelled break: to leave nested loops, return from a function or
    # raise a sentinel — a flag variable is the clumsy third option.


if __name__ == "__main__":
    main()
