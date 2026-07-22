"""Inheritance, `super()`, and why Python rarely needs it.

A subclass inherits every attribute and method, and may override any of them.
`super().method()` calls the next implementation along the *method resolution
order* (MRO) — not necessarily the parent you named, which is what makes
cooperative multiple inheritance and mixins work.

Python's duck typing means inheritance is optional for polymorphism: any
object with the right methods will do. Inherit to share implementation, not
merely to declare a relationship.
"""


class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return f"{self.name} makes a sound"

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name!r})"


class Dog(Animal):
    def speak(self) -> str:  # override
        return f"{self.name} says woof"


class Puppy(Dog):
    def __init__(self, name: str, weeks: int) -> None:
        super().__init__(name)  # run the parent initialiser first
        self.weeks = weeks

    def speak(self) -> str:
        return f"{super().speak()} (softly, at {self.weeks} weeks)"


class Loud:
    """A mixin: no state of its own, just behaviour to compose in."""

    def speak(self) -> str:
        return super().speak().upper()


class LoudDog(Loud, Dog):
    """MRO: LoudDog -> Loud -> Dog -> Animal. Loud.speak calls Dog.speak."""


class Duck:
    """Not an Animal at all — but it quacks the same interface."""

    def speak(self) -> str:
        return "quack"


def main() -> None:
    animals = [Animal("Generic"), Dog("Rex"), Puppy("Bud", 6), LoudDog("Max")]
    for a in animals:
        print(f"{a!r:22} {a.speak()}")

    print(f"MRO: {[c.__name__ for c in LoudDog.__mro__]}")

    print(f"isinstance(Puppy('x', 1), Animal) -> {isinstance(Puppy('x', 1), Animal)}")
    print(f"issubclass(Dog, Animal) -> {issubclass(Dog, Animal)}")

    # Duck typing: polymorphism without a shared base class.
    for speaker in (Dog("Rex"), Duck()):
        print(f"duck-typed: {speaker.speak()}")


if __name__ == "__main__":
    main()
