"""f-strings — formatting by embedding expressions directly in the literal.

Prefix a string with `f` and anything inside `{}` is evaluated as Python and
inserted. After the value you can add a format spec (`:.2f`, `:>10`, `:,`) and
a conversion (`!r` for repr, `!s` for str).

f-strings are the fastest formatting option in Python because the work happens
at compile time, not by parsing a template at runtime.
"""


def main() -> None:
    name, age, ratio = "Ada", 36, 2 / 3

    print(f"{name} is {age} years old")

    # Any expression, not just a name.
    print(f"next year: {age + 1}")
    print(f"upper: {name.upper()}")

    # Format specs: precision, thousands separator, padding, alignment.
    print(f"ratio = {ratio:.3f}")
    print(f"big   = {1234567:,}")
    print(f"|{name:<10}|{name:^10}|{name:>10}|")
    print(f"hex   = {255:#x}   binary = {5:08b}   percent = {ratio:.1%}")

    # !r shows the repr — quotes included. Invaluable when debugging blanks.
    blank = "  "
    print(f"blank as str: {blank}")
    print(f"blank as repr: {blank!r}")

    # The = suffix prints "expression=value", built for quick debugging.
    print(f"{age * 2 = }")

    # Literal braces are doubled.
    print(f"{{not a placeholder}} but {name} is")

    # Multi-line f-strings work; each piece is still evaluated.
    report = (
        f"name:  {name}\n"
        f"age:   {age}\n"
        f"ratio: {ratio:.2f}"
    )
    print(report)


if __name__ == "__main__":
    main()
