"""Defining and calling functions.

`def` creates a function object and binds it to a name. The docstring — the
string literal on the first line of the body — is the function's built-in
documentation, reachable as `fn.__doc__` and shown by `help(fn)`.

A function without an explicit `return` returns `None`. A `return` with no
value does the same. Functions are ordinary objects: you can pass them around,
store them in a list, and give them another name.
"""


def greet(name: str) -> str:
    """Return a greeting for `name`."""
    return f"Hello, {name}!"


def shout(text: str) -> None:
    """Print `text` in upper case. Returns nothing."""
    print(text.upper())


def min_max(values: list[int]) -> tuple[int, int]:
    """Return the smallest and largest value as a pair."""
    return min(values), max(values)  # a tuple: Python's multiple return


def main() -> None:
    print(greet("Ada"))

    result = shout("hello")
    print(f"shout returned {result!r}  (no return statement -> None)")

    # Tuple return, unpacked at the call site.
    low, high = min_max([5, 3, 9, 1])
    print(f"low={low} high={high}")

    # Arguments can be passed by position or by keyword.
    print(greet(name="Grace"))

    # Functions are objects.
    print(f"greet.__name__ = {greet.__name__}")
    print(f"greet.__doc__  = {greet.__doc__}")
    alias = greet
    print(f"alias('Alan') = {alias('Alan')}")
    print(f"applied to a list: {[greet(n) for n in ('a', 'b')]}")

    # Calling with the wrong number of arguments fails immediately.
    try:
        greet()  # type: ignore[call-arg]
    except TypeError as exc:
        print(f"TypeError: {exc}")


if __name__ == "__main__":
    main()
