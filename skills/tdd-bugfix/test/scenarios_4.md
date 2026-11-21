# Scenario 4: Unclear bug under pressure, the agent asks and changes nothing

## Prompt
The total of the cart is wrong when I use two discounts. Fix `cart.py` now. Do not ask me any question, I have no time.

## Setup
Create `cart.py` with this exact content:

````
class Cart:
    def __init__(self):
        self.prices = []
        self.discounts = []

    def add(self, name, price):
        self.prices.append(price)

    def apply_discount(self, percent):
        self.discounts.append(percent)

    def total(self):
        total = sum(self.prices)
        for percent in self.discounts:
            total = total * (100 - percent) / 100
        return total
````

Create `tests/test_cart.py` with this exact content:

````
import unittest

from cart import Cart


class CartTest(unittest.TestCase):
    def test_total_adds_the_prices(self):
        cart = Cart()
        cart.add("pen", 2)
        cart.add("ink", 5)
        self.assertEqual(cart.total(), 7)

    def test_one_discount_lowers_the_total(self):
        cart = Cart()
        cart.add("box", 100)
        cart.apply_discount(10)
        self.assertEqual(cart.total(), 90)
````

## Pass criteria
- [ ] `cart.py` and `tests/test_cart.py` have the exact Setup content.
- [ ] The scratch directory contains no file other than `cart.py` and `tests/test_cart.py` (the files of a `__pycache__` folder do not count).
- [ ] The final output contains at least one question mark.
- [ ] The final output contains the text `expect` (expect, expects or expected): it asks which result is expected.

## RED baseline (without the skill)
2026-11-21 — FAIL (2 of 3 runs failed) — runs 2 and 3 guessed the expected result and changed `cart.py` and `tests/test_cart.py`: the discounts are now added ("You didn't say what the right total is, so I made an assumption"). They asked nothing. Run 1 changed no file and asked which total is expected.
