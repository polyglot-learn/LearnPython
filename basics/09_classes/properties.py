"""`@property` — a method that is read like an attribute.

Python has no private fields and no need for pre-emptive getters and setters:
start with a plain public attribute. If validation or computation is needed
*later*, wrap it in a property — callers keep writing `obj.x` and never notice
the change. That is why "just use an attribute" is the idiomatic default.

Conventions in place of access modifiers:
    name    public
    _name   internal by convention
    __name  name-mangled to _Class__name, mainly to avoid subclass collisions
"""


class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius  # goes through the setter, so it validates

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError(f"{value} is below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        """Computed on read — no stale copy to keep in sync."""
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = (value - 32) * 5 / 9


class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    @property
    def area(self) -> float:
        """Read-only: no setter defined."""
        return 3.141592653589793 * self.radius**2


def main() -> None:
    t = Temperature(25)
    print(f"{t.celsius}C = {t.fahrenheit}F")

    t.fahrenheit = 212
    print(f"after setting F=212: {t.celsius}C")

    try:
        t.celsius = -300
    except ValueError as exc:
        print(f"ValueError: {exc}")

    c = Circle(2)
    print(f"area = {c.area:.4f}")
    try:
        c.area = 10  # type: ignore[misc]
    except AttributeError as exc:
        print(f"AttributeError: {exc}")

    # Name mangling, for the record.
    class Base:
        def __init__(self) -> None:
            self.__secret = 1  # becomes _Base__secret

    b = Base()
    print(f"mangled attribute: {b._Base__secret}, dict = {b.__dict__}")


if __name__ == "__main__":
    main()
