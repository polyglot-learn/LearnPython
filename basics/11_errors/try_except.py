"""`try` / `except` / `else` / `finally` — handling what goes wrong.

Python's culture is EAFP: "easier to ask forgiveness than permission". Try the
operation and handle the failure, rather than testing every precondition first
(LBYL) — the test can go stale between the check and the use anyway.

Four blocks, each with a job:
    try     the code that might fail
    except  runs only on a matching exception
    else    runs only if try succeeded — keep it small, it is not protected
    finally always runs, even on return or an unhandled raise: cleanup goes here
"""


def parse_port(raw: str) -> int:
    try:
        port = int(raw)
    except ValueError:
        print(f"  {raw!r} is not a number, defaulting to 8080")
        return 8080
    else:
        print(f"  parsed {port}")
        return port
    finally:
        print("  (finally always runs)")


def main() -> None:
    parse_port("9000")
    parse_port("nine thousand")

    # Catch specific exceptions. A bare `except:` also swallows KeyboardInterrupt
    # and SystemExit, and `except Exception:` hides bugs you wanted to see.
    data = {"a": 1}
    for key in ("a", "b"):
        try:
            print(f"data[{key!r}] = {data[key]}")
        except KeyError as exc:
            print(f"missing key: {exc}")

    # Several types in one handler, and the exception object itself.
    for value in ("10", "0", "x"):
        try:
            print(f"100/{value} = {100 / int(value)}")
        except (ValueError, ZeroDivisionError) as exc:
            print(f"{type(exc).__name__}: {exc}")

    # EAFP vs LBYL.
    def lbyl(d: dict[str, int], k: str) -> int:
        return d[k] if k in d else 0  # two lookups

    def eafp(d: dict[str, int], k: str) -> int:
        try:
            return d[k]
        except KeyError:
            return 0

    print(f"lbyl={lbyl(data, 'z')} eafp={eafp(data, 'z')}")

    # finally runs even when the try block returns.
    def cleanup_demo() -> str:
        try:
            return "returned from try"
        finally:
            print("  cleanup ran before the value was handed back")

    print(cleanup_demo())


if __name__ == "__main__":
    main()
