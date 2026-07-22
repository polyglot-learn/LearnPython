"""Arithmetic operators, including the two Python adds to the usual set.

`**` is exponentiation and `//` is floor division. Both are real operators,
not library functions, and both work on ints and floats.

Augmented assignment (`+=`, `*=`, ...) updates a name in place. For immutable
values it rebinds the name; for mutable ones like a list it mutates the object
itself — a distinction that surprises people exactly once.
"""


def main() -> None:
    a, b = 17, 5
    print(f"{a} + {b} = {a + b}")
    print(f"{a} - {b} = {a - b}")
    print(f"{a} * {b} = {a * b}")
    print(f"{a} / {b} = {a / b}      (true division -> float)")
    print(f"{a} // {b} = {a // b}     (floor division -> int)")
    print(f"{a} % {b} = {a % b}")
    print(f"{a} ** {b} = {a**b}")

    # Modulo follows the sign of the divisor, unlike C or Java.
    print(f"-17 % 5 = {-17 % 5}   (Python)   vs -2 in C-style languages")

    # Augmented assignment on an immutable value rebinds the name.
    n = 10
    n += 5
    print(f"n = {n}")

    # On a mutable value it mutates in place — aliases see the change.
    xs = [1, 2]
    alias = xs
    xs += [3]
    print(f"xs = {xs}, alias = {alias}  (same list object)")

    # These operators are overloaded for non-numbers too.
    print(f"'ab' * 3 = {'ab' * 3}")
    print(f"[0] * 4 = {[0] * 4}")


if __name__ == "__main__":
    main()
