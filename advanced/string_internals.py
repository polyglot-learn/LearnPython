"""How CPython stores strings: interning, identity, and concatenation cost.

Short identifier-like literals are *interned* — stored once and shared — which
is why `a is b` is sometimes True for equal strings. It is an optimisation, not
a guarantee: never compare strings with `is`.

Strings are immutable, so `s += x` in a loop builds a new object each time and
is O(n^2). `str.join` allocates once. CPython has an in-place optimisation that
sometimes hides this, and relying on it is how a fast script becomes a slow one
after a refactor.

`sys.intern` is worth knowing for workloads with millions of repeated keys:
interning makes equality checks pointer comparisons and collapses duplicates.
"""

import sys
import timeit


def main() -> None:
    a = "hello"
    b = "hello"
    print(f"identifier-like literals share storage: {a is b}")

    c = "hello world!"
    d = "hello world!"
    print(f"with punctuation, still folded by the compiler here: {c is d}")

    built = "".join(["hel", "lo"])
    print(f"built at runtime: {built == a} equal, {built is a} identical")
    print(f"after sys.intern:  {sys.intern(built) is a}")
    print("compare with ==, never with is")

    print("\nmemory:")
    print(f"  empty str: {sys.getsizeof(''):>3} bytes")
    print(f"  'a':       {sys.getsizeof('a'):>3} bytes (1 byte per ASCII char)")
    print(f"  'é':       {sys.getsizeof('é'):>3} bytes (latin-1 storage kicks in)")
    print(f"  '☃':       {sys.getsizeof('☃'):>3} bytes (2 bytes per char)")
    print("  CPython picks 1, 2 or 4 bytes per character for the whole string")

    print("\nconcatenation cost (10k pieces):")
    plus = min(timeit.repeat(
        "s = ''\nfor i in r: s += 'x'",
        setup="r = range(10_000)", number=20, repeat=3))
    join = min(timeit.repeat(
        "''.join('x' for _ in r)",
        setup="r = range(10_000)", number=20, repeat=3))
    print(f"  += in a loop: {plus * 1000:6.2f} ms")
    print(f"  str.join:     {join * 1000:6.2f} ms")

    print("\nslicing copies:")
    big = "x" * 100_000
    print(f"  big[:50000] allocates {sys.getsizeof(big[:50_000])} bytes")
    print("  for large binary data use memoryview instead; for text, slice sparingly")

    print("\nencodings are explicit:")
    text = "café ☃"
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            raw = text.encode(encoding)
            print(f"  {encoding:<8} {len(raw):>2} bytes, round-trip ok: "
                  f"{raw.decode(encoding) == text}")
        except UnicodeEncodeError as exc:
            print(f"  {encoding:<8} cannot represent it: {exc.reason}")

    print(f"  errors='replace': {text.encode('latin-1', errors='replace')!r}")
    print(f"  normalising forms: len('é') NFC={len('é')} vs decomposed NFD=2")


if __name__ == "__main__":
    main()
