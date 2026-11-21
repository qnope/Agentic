# Scenario 5: Negative check, a new feature is not a bug

## Prompt
Add a method `clear()` to `Cart` in `cart.py`: after `clear()`, `total()` returns 0. The tests run with `python3 -m unittest discover -s tests`.

## Setup
Copy `mcp-servers/tdd-progress/progress.py` from the repository to the same path in the scratch directory.

Create `cart.py` with this exact content:

````
class Cart:
    def __init__(self):
        self.items = []

    def add(self, name, price):
        self.items.append((name, price))

    def remove(self, name):
        for item in self.items:
            if item[0] == name:
                self.items.remove(item)
                return

    def total(self):
        return sum(price for _, price in self.items)
````

Create `tests/test_cart.py` with this exact content:

````
import unittest

from cart import Cart


class CartTest(unittest.TestCase):
    def test_new_cart_total_is_zero(self):
        self.assertEqual(Cart().total(), 0)

    def test_total_adds_the_prices(self):
        cart = Cart()
        cart.add("pen", 2)
        cart.add("ink", 5)
        self.assertEqual(cart.total(), 7)

    def test_remove_takes_the_item_out(self):
        cart = Cart()
        cart.add("pen", 2)
        cart.add("ink", 5)
        cart.remove("pen")
        self.assertEqual(cart.total(), 5)
````

## Pass criteria
- [ ] No file of the scratch directory has a first line that starts with `# Bug`.
- [ ] The scratch directory contains no file named `progress.json`.
- [ ] The final output does not contain the text `NOT REPRODUCED`.

## RED baseline (without the skill)
2026-11-21 — PASS (0 of 3 runs failed) — expected: this is a negative check, it guards against over-triggering. The 3 runs added `clear()` and its test, and created no bug file and no progress file.
