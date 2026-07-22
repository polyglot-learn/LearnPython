"""Testing with `unittest` — assertions, fixtures, and mocks, no dependencies.

Structure: subclass `TestCase`, write `test_*` methods, use the `assert*`
helpers (they produce far better failure messages than a bare `assert`).
`setUp`/`tearDown` run per test; `subTest` keeps a parameterised loop from
stopping at the first failure.

`unittest.mock` replaces a collaborator so a test does not hit the network,
the clock, or the filesystem. `patch` swaps a name *where it is looked up*,
not where it is defined — the single most common mocking mistake.
"""

import unittest
from unittest.mock import MagicMock, patch


def fetch_price(client, symbol: str) -> float:
    """The unit under test: pure logic around an injected collaborator."""
    raw = client.get(symbol)
    if raw is None:
        raise LookupError(f"no price for {symbol}")
    return round(float(raw) * 1.2, 2)


class Cart:
    def __init__(self) -> None:
        self.items: list[tuple[str, float]] = []

    def add(self, name: str, price: float) -> None:
        if price < 0:
            raise ValueError("price must be non-negative")
        self.items.append((name, price))

    def total(self) -> float:
        return round(sum(price for _, price in self.items), 2)


class TestCart(unittest.TestCase):
    def setUp(self) -> None:
        self.cart = Cart()  # a fresh cart per test

    def test_empty_total(self) -> None:
        self.assertEqual(self.cart.total(), 0)

    def test_add_and_total(self) -> None:
        self.cart.add("apple", 1.5)
        self.cart.add("pear", 2.25)
        self.assertAlmostEqual(self.cart.total(), 3.75)
        self.assertIn(("apple", 1.5), self.cart.items)

    def test_negative_price_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.cart.add("bad", -1)
        self.assertIn("non-negative", str(ctx.exception))

    def test_many_cases(self) -> None:
        for price, expected in [(1, 1), (2.5, 2.5), (0, 0)]:
            with self.subTest(price=price):  # each case reported separately
                cart = Cart()
                cart.add("x", price)
                self.assertEqual(cart.total(), expected)


class TestFetchPrice(unittest.TestCase):
    def test_uses_the_client(self) -> None:
        client = MagicMock()
        client.get.return_value = "10.00"
        self.assertEqual(fetch_price(client, "ACME"), 12.0)
        client.get.assert_called_once_with("ACME")

    def test_missing_price(self) -> None:
        client = MagicMock()
        client.get.return_value = None
        with self.assertRaises(LookupError):
            fetch_price(client, "NOPE")

    def test_patching_a_name(self) -> None:
        with patch(f"{__name__}.fetch_price", return_value=99.0) as stub:
            self.assertEqual(fetch_price(None, "X"), 99.0)
            stub.assert_called_once()


def main() -> None:
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"ran {result.testsRun}, failures {len(result.failures)}, "
          f"errors {len(result.errors)}")


if __name__ == "__main__":
    main()
