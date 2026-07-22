"""`collections` — the specialised containers worth knowing.

    deque            O(1) appends and pops at both ends, optional maxlen
    Counter          multiset with most_common, arithmetic between counters
    defaultdict      a factory runs on a missing key instead of raising
    OrderedDict      still useful for move_to_end and order-sensitive equality
    ChainMap         layered lookup over several mappings, no copying
    namedtuple       a lightweight immutable record with field names

Reaching for the right one usually deletes five lines of bookkeeping and a
class of bugs with it.
"""

from collections import ChainMap, Counter, OrderedDict, defaultdict, deque, namedtuple


def as_plain(d: defaultdict) -> dict:
    return {k: dict(v) for k, v in d.items()}


def main() -> None:
    print("deque:")
    dq = deque([2, 3, 4])
    dq.appendleft(1)
    dq.append(5)
    dq.rotate(2)
    print(f"  rotated: {list(dq)}, popleft {dq.popleft()}")
    tail = deque(maxlen=3)
    tail.extend(range(10))
    print(f"  maxlen=3 keeps the last three: {list(tail)}")

    print("Counter:")
    counts = Counter("mississippi")
    print(f"  most_common(2): {counts.most_common(2)}")
    print(f"  arithmetic: {Counter('aab') + Counter('abc')}")
    print(f"  subtraction drops non-positives: {Counter('aab') - Counter('ab')}")
    print(f"  total: {counts.total()}, missing key returns {counts['z']}")

    print("defaultdict:")
    groups: defaultdict[int, list[str]] = defaultdict(list)
    for word in ("apple", "fig", "pear", "kiwi", "plum"):
        groups[len(word)].append(word)
    print(f"  by length: {dict(groups)}")
    nested: defaultdict[str, defaultdict[str, int]] = defaultdict(lambda: defaultdict(int))
    nested["a"]["x"] += 1
    print(f"  nested autovivification: {as_plain(nested)}")

    print("OrderedDict:")
    od = OrderedDict(a=1, b=2, c=3)
    od.move_to_end("a")
    print(f"  moved 'a' last: {list(od)}, popitem(last=False) -> {od.popitem(last=False)}")
    print(f"  order-sensitive equality: "
          f"{OrderedDict(a=1, b=2) == OrderedDict(b=2, a=1)} vs dict "
          f"{dict(a=1, b=2) == dict(b=2, a=1)}")

    print("ChainMap:")
    defaults = {"colour": "black", "size": "M"}
    user = {"size": "L"}
    settings = ChainMap(user, defaults)  # first mapping wins
    print(f"  resolved: size={settings['size']} colour={settings['colour']}")
    print(f"  writes go to the first map: ", end="")
    settings["colour"] = "red"
    print(f"user={user}, defaults untouched={defaults}")

    print("namedtuple:")
    Point = namedtuple("Point", "x y")
    p = Point(3, 4)
    print(f"  {p}, unpacks {tuple(p)}, _replace -> {p._replace(y=10)}, "
          f"_asdict -> {p._asdict()}")


if __name__ == "__main__":
    main()
