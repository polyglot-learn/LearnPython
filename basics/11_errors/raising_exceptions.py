"""Raising — failing loudly, and keeping the cause.

`raise SomeError("message")` signals a problem the current code cannot handle.
Pick the type that fits: ValueError for a bad value, TypeError for a wrong
type, KeyError/IndexError for a missing element, NotImplementedError for a
stub.

Two forms worth distinguishing when re-raising:
    raise NewError(...) from exc   explicit cause: "this happened *because of* that"
    raise                          re-raise the current exception, traceback intact

Never `except: pass`. A swallowed exception is a bug that will resurface
somewhere far from its origin.
"""


class ConfigError(Exception):
    """Raised when configuration cannot be loaded."""


def set_age(age: int) -> int:
    if not isinstance(age, int):
        raise TypeError(f"age must be an int, got {type(age).__name__}")
    if age < 0:
        raise ValueError(f"age must be non-negative, got {age}")
    return age


def load_port(config: dict[str, str]) -> int:
    try:
        return int(config["port"])
    except KeyError as exc:
        raise ConfigError("no 'port' in config") from exc
    except ValueError as exc:
        raise ConfigError(f"port is not a number: {config['port']!r}") from exc


def main() -> None:
    for candidate in (30, -1, "x"):
        try:
            print(f"set_age({candidate!r}) = {set_age(candidate)}")  # type: ignore[arg-type]
        except (TypeError, ValueError) as exc:
            print(f"{type(exc).__name__}: {exc}")

    for config in ({"port": "8080"}, {}, {"port": "http"}):
        try:
            print(f"port = {load_port(config)}")
        except ConfigError as exc:
            print(f"ConfigError: {exc}  (caused by {type(exc.__cause__).__name__})")

    # Bare `raise` re-raises without losing the traceback — the right way to
    # log and rethrow.
    def log_and_rethrow() -> None:
        try:
            1 / 0
        except ZeroDivisionError:
            print("  logging, then re-raising unchanged")
            raise

    try:
        log_and_rethrow()
    except ZeroDivisionError as exc:
        print(f"caught again: {exc}")

    # assert states an invariant. It is stripped by `python -O`, so never use
    # it to validate untrusted input — only to catch programmer error.
    total = 10
    assert total > 0, "total must be positive"
    print("assert passed")


if __name__ == "__main__":
    main()
