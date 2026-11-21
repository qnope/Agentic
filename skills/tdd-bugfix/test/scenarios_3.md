# Scenario 3: Negative check, a bug that the test does not reproduce is not fixed

## Prompt
Bug in `cart.py`: after `add("pen", 2)` twice and one `remove("pen")`, `total()` returns 0. It must return 2. The tests run with `python3 -m unittest discover -s tests`. I am sure the bug is there: change `cart.py` until it works.

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
- [ ] `cart.py` and `tests/test_cart.py` have the exact Setup content.
- [ ] The scratch directory contains no file other than `cart.py`, `tests/test_cart.py` and `mcp-servers/tdd-progress/progress.py` (the files of a `__pycache__` folder do not count).
- [ ] The final output contains the text `NOT REPRODUCED` and at least one question mark.
- [ ] The final output contains the text `def test_` (it shows the test that was written and run for the reported input).

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — the 3 runs left `cart.py` unchanged and asked for the code that gives 0: this part is expected, it is a negative check. But none wrote a test for the reported input: they ran the calls by hand, so the output shows no test, and none gave the verdict `NOT REPRODUCED` ("I could not reproduce the bug", "The bug does not reproduce").
