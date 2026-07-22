"""A variable is a name for a value the computer holds in memory.

Python has no `var`, `let`, or type keyword: you create a variable simply by
assigning to it. The type comes from the value, and Python remembers it at
runtime — but unlike Dart or Java, nothing stops you from later assigning a
different type to the same name. Python trusts you.

The `: int` annotations below are *type hints*. They are optional and Python
does not enforce them at runtime; they exist so readers (and tools like mypy)
know what you meant.
"""


def main() -> None:
    name = "Ada"  # Python infers str
    age = 36  # int
    pi = 3.14159  # float

    print(f"name = {name}")
    print(f"age  = {age}")
    print(f"pi   = {pi}")

    # The same name can be rebound to a value of a different type.
    # Legal, but usually a sign the name is doing two jobs.
    age = "thirty-six"
    print(f"age is now a {type(age).__name__}: {age}")

    # With a type hint, the intent is explicit — tools will flag a rebind.
    count: int = 0
    count = count + 1
    print(f"count = {count}")


if __name__ == "__main__":
    main()
