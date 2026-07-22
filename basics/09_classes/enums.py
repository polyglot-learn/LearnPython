"""`Enum` — a fixed set of named constants, checkable and self-documenting.

Bare string or int constants let typos through silently: `status = "activ"`
is a runtime mystery. An enum member is a real object, so a wrong name fails
immediately, and the type shows up in signatures and `match` statements.

Variants worth knowing:
    Enum        the general case
    IntEnum     members are also ints, for interop with C APIs or JSON
    StrEnum     members are also strs (3.11+)
    Flag        combinable bit flags
    auto()      "I do not care about the value, just the name"
"""

from enum import Enum, Flag, IntEnum, auto


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 5
    HIGH = 10


class Direction(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()

    @property
    def opposite(self) -> "Direction":
        pairs = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }
        return pairs[self]


class Permission(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()


def main() -> None:
    print(f"Color.RED = {Color.RED}, name = {Color.RED.name}, value = {Color.RED.value}")
    print(f"all members: {[c.name for c in Color]}")
    print(f"lookup by value: {Color('green')}")
    print(f"lookup by name:  {Color['BLUE']}")

    try:
        Color("purple")
    except ValueError as exc:
        print(f"ValueError: {exc}")

    # Identity comparison is the idiom; members are singletons.
    print(f"Color.RED is Color('red') -> {Color.RED is Color('red')}")

    # IntEnum members compare and sort as ints.
    print(f"Priority.HIGH > Priority.LOW -> {Priority.HIGH > Priority.LOW}")
    print(f"as int: {Priority.MEDIUM + 1}")

    print(f"Direction.NORTH.opposite = {Direction.NORTH.opposite}")

    # Flags combine with | and test with in.
    perms = Permission.READ | Permission.WRITE
    print(f"perms = {perms}, writable: {Permission.WRITE in perms}, "
          f"executable: {Permission.EXECUTE in perms}")

    # Enums pair naturally with match.
    for c in Color:
        match c:
            case Color.RED:
                print("  stop")
            case Color.GREEN:
                print("  go")
            case _:
                print(f"  {c.value}: no rule")


if __name__ == "__main__":
    main()
