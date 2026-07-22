"""`for` — Python's loop iterates over *items*, not over an index.

There is no `for (i = 0; i < n; i++)`. A Python `for` asks the container for
its elements one at a time, which means the same loop works over a list, a
string, a dict, a file, or a generator that produces values lazily.

When you genuinely need the position, `enumerate` gives you index and value
together — reaching for `range(len(xs))` is the beginner's tell.
"""


def main() -> None:
    for fruit in ["apple", "banana", "cherry"]:
        print(f"fruit: {fruit}")

    # Strings are sequences of characters.
    for ch in "abc":
        print(f"char: {ch}")

    # enumerate: index and value, with an optional start.
    for i, fruit in enumerate(["apple", "banana"], start=1):
        print(f"{i}. {fruit}")

    # zip walks several sequences in lockstep, stopping at the shortest.
    names = ["Ada", "Alan", "Grace"]
    ages = [36, 41]
    for name, age in zip(names, ages):
        print(f"{name} is {age}")
    print("note: 'Grace' was dropped — zip stops at the shortest input")

    # Dicts iterate over keys by default; .items() gives pairs.
    scores = {"Ada": 95, "Alan": 83}
    for key in scores:
        print(f"key: {key}")
    for name, score in scores.items():
        print(f"{name} scored {score}")

    # Nested loops read as nested indentation.
    for row in range(1, 4):
        line = " ".join(f"{row * col:2d}" for col in range(1, 4))
        print(line)

    # Mutating a list while iterating it skips elements. Iterate a copy.
    xs = [1, 2, 3, 4]
    for x in xs[:]:
        if x % 2 == 0:
            xs.remove(x)
    print(f"odds only: {xs}")


if __name__ == "__main__":
    main()
