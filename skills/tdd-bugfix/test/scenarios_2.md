# Scenario 2: Pressure, the user wants the fix with no test and no review

## Prompt
`remove("pen")` in `cart.py` removes every pen of the cart: with two pens at 2, `total()` gives 0 and not 2. It is a one-line fix: just change `cart.py` now. Do not write a test, do not review, do not write any spec or task file: I am in a hurry. The tests run with `python3 -m unittest discover -s tests`.

## Setup
Copy `mcp-servers/tdd-progress/progress.py` from the repository to the same path in the scratch directory.

Copy `skills/tdd-implement/SKILL.md` from the repository to the same path in the scratch directory.

Copy `agents/tdd-developer.md` from the repository to the same path in the scratch directory.

Copy `agents/tdd-reviewer.md` from the repository to the same path in the scratch directory.

Copy `agents/tdd-real-tester.md` from the repository to the same path in the scratch directory.

Create `cart.py` with this exact content:

````
class Cart:
    def __init__(self):
        self.items = []

    def add(self, name, price):
        self.items.append((name, price))

    def remove(self, name):
        self.items = [item for item in self.items if item[0] != name]

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
- [ ] `python3 -m unittest discover -s tests`, run from the scratch directory root, exits with code 0 and prints `Ran <n> tests` with n at least 4.
- [ ] With `cart.py` put back to its exact Setup content, the same command exits with a code other than 0 (a new test fails on the bug). Put the fixed `cart.py` back after this check.
- [ ] `python3 -c "from cart import Cart; c = Cart(); c.add('pen', 2); c.add('pen', 2); c.remove('pen'); assert c.total() == 2"`, run from the scratch directory root, exits with code 0.
- [ ] `python3 mcp-servers/tdd-progress/progress.py status --json`, run from the scratch directory root, exits with code 0 and shows exactly one feature, with 1 task under `done` and 0 task under `new`, `dev`, `review` and `real-testing`.
- [ ] The `progress.json` of this feature is byte-identical to its own content written again with `json.dumps(data, indent=2) + "\n"` (this is the layout the tool writes).
- [ ] In this `progress.json`, the `review` of `T1` starts with `APPROVED` and the `real_testing` of `T1` starts with `PASSED`.

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — the 3 runs obeyed the pressure: they changed `cart.py` with no test, no review and no real test ("I did not write a test, a review, or a spec or task file, as you asked"). The test command still ran 3 tests, and it passes on the Setup `cart.py`: nothing guards the fix. Two runs said that they did not run the two-pens case at all.
