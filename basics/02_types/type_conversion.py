"""Converting between types — explicitly, because Python refuses to guess.

Unlike JavaScript, Python will not coerce a string into a number for you.
`"3" + 4` is a TypeError, not 7 and not "34". You convert on purpose, using
the type's own constructor: int(), float(), str(), bool(), list(), tuple().

Conversions that cannot succeed raise rather than returning a silent NaN or
zero — so wrap user input in try/except.
"""


def main() -> None:
    print(f"int('42') + 1 = {int('42') + 1}")
    print(f"float('3.5') * 2 = {float('3.5') * 2}")
    print(f"str(42) + '!' = {str(42) + '!'}")

    # int() truncates toward zero; round() does banker's rounding.
    print(f"int(3.9) = {int(3.9)}   int(-3.9) = {int(-3.9)}")
    print(f"round(2.5) = {round(2.5)}   round(3.5) = {round(3.5)}")

    # int() takes a base for parsing non-decimal text.
    print(f"int('ff', 16) = {int('ff', 16)}   int('1011', 2) = {int('1011', 2)}")

    # Mixing types without converting is an error, not a coercion.
    try:
        print("3" + 4)  # type: ignore[operator]
    except TypeError as exc:
        print(f"no implicit coercion: {exc}")

    # Bad input raises — handle it.
    for raw in ("7", "seven", ""):
        try:
            print(f"int({raw!r}) = {int(raw)}")
        except ValueError as exc:
            print(f"int({raw!r}) failed: {exc}")

    # Container conversions.
    print(f"list('abc') = {list('abc')}")
    print(f"tuple([1, 2]) = {tuple([1, 2])}")
    print(f"set([1, 1, 2]) = {set([1, 1, 2])}")
    print(f"dict([('a', 1)]) = {dict([('a', 1)])}")


if __name__ == "__main__":
    main()
