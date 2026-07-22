"""Dunder methods — how your class plugs into Python's syntax.

`len(x)` calls `x.__len__()`. `a + b` calls `a.__add__(b)`. `x in c` calls
`c.__contains__(x)`. Implementing these "double underscore" methods is how a
custom type earns the same syntax the built-ins get.

Two pairs to get right:
  __repr__ / __str__  — repr is for developers (unambiguous, ideally
                        eval-able); str is for users. Define __repr__ first;
                        __str__ falls back to it.
  __eq__  / __hash__  — defining __eq__ sets __hash__ to None, making the
                        object unhashable. Define both, over the same fields.
"""


class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented  # lets Python try the reflected operation
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, k: float) -> "Vector":
        return Vector(self.x * k, self.y * k)

    def __rmul__(self, k: float) -> "Vector":
        return self * k  # makes `2 * v` work, not just `v * 2`

    def __abs__(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5

    def __len__(self) -> int:
        return 2

    def __getitem__(self, index: int) -> float:
        return (self.x, self.y)[index]

    def __bool__(self) -> bool:
        return bool(self.x or self.y)


def main() -> None:
    a, b = Vector(1, 2), Vector(3, 4)

    print(f"repr : {a!r}")
    print(f"str  : {a}")
    print(f"a + b: {a + b}")
    print(f"a * 3: {a * 3}   3 * a: {3 * a}")
    print(f"abs(b): {abs(b)}")
    print(f"a == Vector(1, 2): {a == Vector(1, 2)}")
    print(f"hashable: {len({a, Vector(1, 2), b})} unique in a set")

    # __getitem__ alone makes the object indexable *and* iterable.
    print(f"a[0] = {a[0]}, unpacked = {tuple(a)}, len = {len(a)}")

    print(f"bool(Vector(0, 0)) = {bool(Vector(0, 0))}, bool(a) = {bool(a)}")

    # Without __eq__ the default is identity comparison.
    class Plain:
        pass

    print(f"default equality is identity: {Plain() == Plain()}")


if __name__ == "__main__":
    main()
