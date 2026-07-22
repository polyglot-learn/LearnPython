"""Python has no `const`. It has a naming convention instead.

A name in ALL_CAPS means "treat this as a constant — do not reassign it".
Nothing in the language enforces that; it is a promise between programmers.

For values that must *really* not change, reach for an immutable type: a
tuple instead of a list, a frozenset instead of a set. Immutability is a
property of the value, not of the name that points at it.

Naming rules that matter:
  - variables and functions: lower_snake_case
  - constants:               UPPER_SNAKE_CASE
  - classes:                 CapWords
  - a leading underscore (_private) means "internal, do not touch"
"""

MAX_RETRIES = 3
SUPPORTED_UNITS = ("m", "km", "mi")  # tuple: immutable, cannot be appended to


def main() -> None:
    print(f"MAX_RETRIES = {MAX_RETRIES}")
    print(f"SUPPORTED_UNITS = {SUPPORTED_UNITS}")

    # The convention is not enforced — this reassignment is legal Python.
    # It is also exactly what the ALL_CAPS name is asking you not to do.
    # MAX_RETRIES = 5

    # The tuple, on the other hand, genuinely cannot be modified.
    try:
        SUPPORTED_UNITS[0] = "ft"  # type: ignore[index]
    except TypeError as exc:
        print(f"tuple is immutable: {exc}")

    mutable_units = ["m", "km", "mi"]
    mutable_units[0] = "ft"  # a list has no such protection
    print(f"list is mutable: {mutable_units}")


if __name__ == "__main__":
    main()
