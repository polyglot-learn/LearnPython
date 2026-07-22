"""`pickle` — Python-native serialisation, and why it is not a data format.

Pickle can round-trip almost any Python object, including cycles and custom
classes, by recording *instructions to rebuild them*. That is also the danger:
unpickling executes those instructions, so loading an untrusted pickle is
equivalent to running untrusted code. Use JSON across trust boundaries.

Hooks worth knowing: `__getstate__`/`__setstate__` control what is saved,
`__reduce__` controls how the object is reconstructed. Anything unpicklable
(a socket, a file handle, a lock) must be dropped in `__getstate__`.
"""

import json
import pickle
import pickletools


class Connection:
    """Holds a resource that must not be serialised."""

    def __init__(self, host: str) -> None:
        self.host = host
        self.socket = object()  # stands in for something unpicklable
        self.cache: dict[str, int] = {"hits": 0}

    def __getstate__(self) -> dict:
        state = self.__dict__.copy()
        del state["socket"]  # drop the live resource
        return state

    def __setstate__(self, state: dict) -> None:
        self.__dict__.update(state)
        self.socket = object()  # rebuild on load

    def __repr__(self) -> str:
        return f"Connection({self.host!r}, cache={self.cache})"


def main() -> None:
    data = {"name": "Ada", "scores": [1, 2, 3], "nested": {"ok": True}}
    blob = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"pickled {len(blob)} bytes, protocol {pickle.HIGHEST_PROTOCOL}")
    print(f"round-trip equal: {pickle.loads(blob) == data}")
    print(f"json for the same data: {len(json.dumps(data))} bytes, but text and portable")

    # Cycles are handled; JSON cannot express them at all.
    cyclic: list = [1, 2]
    cyclic.append(cyclic)
    restored = pickle.loads(pickle.dumps(cyclic))
    print(f"cycle preserved: {restored[2] is restored}")
    try:
        json.dumps(cyclic)
    except ValueError as exc:
        print(f"json refuses: {exc}")

    # Custom state hooks.
    conn = Connection("db.internal")
    conn.cache["hits"] = 7
    revived = pickle.loads(pickle.dumps(conn))
    print(f"revived {revived}, new socket: {revived.socket is not conn.socket}")

    # Not everything is picklable.
    try:
        pickle.dumps(lambda x: x)
    except (AttributeError, pickle.PicklingError) as exc:
        print(f"lambdas are not picklable: {type(exc).__name__}")

    # The bytecode a pickle really is.
    print("pickle opcodes for {'a': 1}:")
    pickletools.dis(pickle.dumps({"a": 1}, protocol=0))

    print("NEVER unpickle data you did not produce — it can execute code")


if __name__ == "__main__":
    main()
