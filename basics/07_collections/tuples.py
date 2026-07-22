"""`tuple` — an immutable sequence, and Python's lightweight record.

A tuple is defined by the commas, not the parentheses: `1, 2` is already a
tuple. A one-element tuple therefore needs the trailing comma: `(1,)`.

Because tuples are immutable they are hashable (as long as their contents
are), which lets them be dict keys and set members — something a list can
never do. Use a tuple for a fixed-size record, a list for a growable series.
"""

from collections import namedtuple


def main() -> None:
    point = (3, 4)
    print(f"point = {point}, x = {point[0]}, len = {len(point)}")

    # The comma makes the tuple; the parentheses only group.
    bare = 1, 2, 3
    single = (1,)
    not_a_tuple = (1)
    print(f"bare = {bare}, single = {single}, (1) is just an int: {not_a_tuple!r}")

    # Immutable: no append, no item assignment.
    try:
        point[0] = 9  # type: ignore[index]
    except TypeError as exc:
        print(f"immutable: {exc}")

    # ...but a tuple can *hold* a mutable object, which stays mutable.
    mixed = ([1, 2], "fixed")
    mixed[0].append(3)
    print(f"tuple holding a list: {mixed}")

    # Hashable, so usable as a dict key or set member.
    distances = {(0, 0): 0, (3, 4): 5}
    print(f"distances[(3, 4)] = {distances[(3, 4)]}")
    try:
        {[0, 0]: 0}  # type: ignore[dict-item]
    except TypeError as exc:
        print(f"a list cannot be a key: {exc}")

    # Unpacking is where tuples shine — including in for loops.
    for name, age in [("Ada", 36), ("Alan", 41)]:
        print(f"{name} is {age}")

    # namedtuple: the same immutability, with field names.
    Point = namedtuple("Point", "x y")
    p = Point(3, 4)
    print(f"{p} -> p.x = {p.x}, as tuple: {tuple(p)}, replaced: {p._replace(x=10)}")


if __name__ == "__main__":
    main()
