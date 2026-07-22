"""Two ways to describe an interface: ABCs and Protocols.

An **abstract base class** (`abc.ABC`) is nominal: a subclass must inherit from
it, and Python refuses to instantiate the class until every `@abstractmethod`
is implemented. Use it when you also want to share code with subclasses.

A **Protocol** (`typing.Protocol`) is structural: any class with matching
methods satisfies it, no inheritance required. It is duck typing that a static
checker can verify — usually the better fit for Python code you do not own.
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


class Shape(ABC):
    """Abstract: cannot be instantiated, and shares concrete helpers."""

    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    def describe(self) -> str:  # concrete, inherited by every shape
        return f"{type(self).__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"


class Rectangle(Shape):
    def __init__(self, w: float, h: float) -> None:
        self.w, self.h = w, h

    def area(self) -> float:
        return self.w * self.h

    def perimeter(self) -> float:
        return 2 * (self.w + self.h)


class Circle(Shape):
    def __init__(self, r: float) -> None:
        self.r = r

    def area(self) -> float:
        return 3.141592653589793 * self.r**2

    def perimeter(self) -> float:
        return 2 * 3.141592653589793 * self.r


class Incomplete(Shape):
    def area(self) -> float:
        return 0.0  # perimeter() left unimplemented


@runtime_checkable
class Drawable(Protocol):
    """Structural: anything with draw() -> str qualifies."""

    def draw(self) -> str: ...


class Sprite:  # note: inherits nothing
    def draw(self) -> str:
        return "<sprite>"


def render(item: Drawable) -> None:
    print(f"  render -> {item.draw()}")


def main() -> None:
    for shape in (Rectangle(3, 4), Circle(1)):
        print(shape.describe())

    try:
        Incomplete()  # type: ignore[abstract]
    except TypeError as exc:
        print(f"TypeError: {exc}")

    render(Sprite())
    print(f"isinstance(Sprite(), Drawable) -> {isinstance(Sprite(), Drawable)}")
    print(f"Sprite inherits Drawable? {Drawable in Sprite.__mro__}")


if __name__ == "__main__":
    main()
