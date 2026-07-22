"""`is` / `is not` and `in` / `not in`.

`==` asks "do these have the same value?". `is` asks "are these the same
object in memory?". They agree often enough to hide the difference, and then
disagree at the worst moment — so use `is` only for singletons: None, True,
False, and sentinel objects you created yourself.

`in` tests membership. Its cost depends entirely on the container: O(n) for a
list or tuple, O(1) average for a set or dict.
"""


def main() -> None:
    a = [1, 2, 3]
    b = [1, 2, 3]
    c = a

    print(f"a == b -> {a == b}   (same contents)")
    print(f"a is b -> {a is b}   (different objects)")
    print(f"a is c -> {a is c}   (c is just another name for a)")
    print(f"id(a)={id(a) == id(c)} matches id(c)")

    # Small ints and short strings are cached by CPython, which makes `is`
    # *appear* to work on values. Do not rely on it — it is an implementation
    # detail that changes with the literal.
    print(f"256 is 256 -> {256 is 256}")
    big1 = 1000
    big2 = 10**3
    print(f"1000 is 10**3 -> {big1 is big2}  (cache does not cover this)")

    # The correct use of `is`: singletons.
    value = None
    print(f"value is None -> {value is None}")

    # Membership.
    print(f"2 in a -> {2 in a}")
    print(f"9 not in a -> {9 not in a}")
    print(f"'ell' in 'hello' -> {'ell' in 'hello'}  (substring check)")

    # On a dict, `in` looks at keys, not values.
    ages = {"Ada": 36, "Alan": 41}
    print(f"'Ada' in ages -> {'Ada' in ages}")
    print(f"36 in ages -> {36 in ages}   36 in ages.values() -> {36 in ages.values()}")

    # Container choice decides the cost of `in`.
    print("list/tuple membership: O(n) scan; set/dict membership: O(1) hash")


if __name__ == "__main__":
    main()
