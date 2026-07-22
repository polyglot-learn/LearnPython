"""Default parameter values — and the one famous trap.

A default is evaluated **once**, when the `def` statement runs, not on every
call. For an immutable default (0, None, "x") that is invisible. For a mutable
default (`[]`, `{}`) it means every call shares the *same* object, so state
leaks between calls.

The fix is always the same: default to `None` and build the real value inside.
"""


def add_item(item: str, basket: list[str] = []) -> list[str]:
    """BUGGY: the default list is created once and shared by all callers."""
    basket.append(item)
    return basket


def add_item_safe(item: str, basket: list[str] | None = None) -> list[str]:
    """Correct: a fresh list per call when the caller supplies none."""
    if basket is None:
        basket = []
    basket.append(item)
    return basket


def connect(host: str, port: int = 5432, *, timeout: float = 3.0) -> str:
    """Anything after `*` must be passed by keyword — good for options."""
    return f"{host}:{port} (timeout {timeout}s)"


def main() -> None:
    print("shared mutable default:")
    print(f"  {add_item('apple')}")
    print(f"  {add_item('banana')}   <- the apple is still there")

    print("None sentinel:")
    print(f"  {add_item_safe('apple')}")
    print(f"  {add_item_safe('banana')}")

    print(connect("db.internal"))
    print(connect("db.internal", 6432))
    print(connect("db.internal", timeout=0.5))

    # A keyword-only parameter cannot be passed positionally.
    try:
        connect("db.internal", 5432, 1.0)  # type: ignore[misc]
    except TypeError as exc:
        print(f"TypeError: {exc}")

    # The defaults are visible on the function object — same list every time.
    print(f"add_item.__defaults__ = {add_item.__defaults__}")


if __name__ == "__main__":
    main()
