"""`dict` — key/value mapping with O(1) average lookup.

Keys must be hashable (str, int, tuple — not list). Since Python 3.7 a dict
preserves insertion order, so iterating one is deterministic.

`d[key]` raises KeyError when the key is missing; `d.get(key, default)` does
not. Which one you want is a design decision: raise when absence is a bug,
default when absence is normal.
"""

from collections import Counter, defaultdict


def main() -> None:
    ages = {"Ada": 36, "Alan": 41}
    ages["Grace"] = 45
    print(f"ages = {ages}")

    print(f"ages['Ada'] = {ages['Ada']}")
    print(f"ages.get('Nobody') = {ages.get('Nobody')}")
    print(f"ages.get('Nobody', 0) = {ages.get('Nobody', 0)}")
    try:
        ages["Nobody"]
    except KeyError as exc:
        print(f"KeyError: {exc}")

    print(f"keys   = {list(ages.keys())}")
    print(f"values = {list(ages.values())}")
    print(f"items  = {list(ages.items())}")

    # setdefault: read-or-insert in one step.
    ages.setdefault("Katherine", 0)
    print(f"after setdefault: {ages}")

    removed = ages.pop("Katherine")
    print(f"popped {removed}, now {ages}")

    # Merging: | (3.9+) makes a new dict, |= updates in place.
    print(f"merged: {ages | {'Ada': 99, 'Barbara': 30}}")

    # Grouping, three ways.
    words = ["apple", "avocado", "banana", "blueberry", "cherry"]
    grouped: dict[str, list[str]] = {}
    for w in words:
        grouped.setdefault(w[0], []).append(w)
    print(f"setdefault grouping: {grouped}")

    auto: defaultdict[str, list[str]] = defaultdict(list)
    for w in words:
        auto[w[0]].append(w)
    print(f"defaultdict grouping: {dict(auto)}")

    print(f"Counter: {Counter('mississippi').most_common(3)}")

    # Dict comprehension, and inverting a mapping.
    squares = {n: n * n for n in range(1, 6)}
    print(f"squares = {squares}")
    print(f"inverted = { {v: k for k, v in squares.items()} }")


if __name__ == "__main__":
    main()
