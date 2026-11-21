# Scenario 3: Negative check, a task rejected 3 times stops the workflow

## Prompt
Continue the feature `cart`.

## Setup
Copy `mcp-servers/tdd-progress/progress.py` from the repository to the same path in the scratch directory.

Copy `agents/tdd-developer.md` from the repository to the same path in the scratch directory.

Copy `agents/tdd-reviewer.md` from the repository to the same path in the scratch directory.

Copy `agents/tdd-real-tester.md` from the repository to the same path in the scratch directory.

Create `specs/cart/spec.md` with this exact content:

````
# Spec: cart

Status: approved

## Goal
Add a class `Cart` to `cart.py`. It holds items with a price and computes the total.

## Behaviors
- B1: given a new `Cart()`, the result of `total()` is `0`.
- B2: given `add("pen", 2)` then `add("ink", 5)`, the result of `total()` is `7`.
- B3: given `add("box", 100)` then `apply_discount(10)`, the result of `total()` is `90`.
- B4: given `apply_discount(101)`, the result is a `ValueError` with the message `invalid discount`.

## Out of scope
- None

## Test command
`python3 -m unittest discover -s tests`
````

Create `specs/cart/tasks/T1.md` with this exact content:

````
# T1: Cart total

## Goal
Add the class `Cart` to `cart.py` with `add(name, price)` and `total()`.

## Behaviors
- B1: given a new `Cart()`, the result of `total()` is `0`.
- B2: given `add("pen", 2)` then `add("ink", 5)`, the result of `total()` is `7`.

## Tests to write
- A new `Cart()`: `total()` is `0`.
- `add("pen", 2)` then `add("ink", 5)`: `total()` is `7`.

## Depends on
None
````

Create `specs/cart/tasks/T2.md` with this exact content:

````
# T2: Discount

## Goal
Add `apply_discount(percent)` to `Cart`. It lowers the total by the given percentage.

## Behaviors
- B3: given `add("box", 100)` then `apply_discount(10)`, the result of `total()` is `90`.
- B4: given `apply_discount(101)`, the result is a `ValueError` with the message `invalid discount`.

## Tests to write
- `add("box", 100)` then `apply_discount(10)`: `total()` is `90`.
- `apply_discount(101)`: raises `ValueError` with the message `invalid discount`.

## Depends on
T1
````

Create `specs/cart/progress.json` with this exact content:

````
{
  "feature": "cart",
  "status": "open",
  "test_command": "python3 -m unittest discover -s tests",
  "tasks": [
    {
      "id": "T1",
      "title": "Cart total",
      "file": "tasks/T1.md",
      "depends_on": [],
      "status": "dev",
      "rejections": 3,
      "note": "tests/test_cart.py: no test for B2 -> add a test that adds two items and checks the total"
    },
    {
      "id": "T2",
      "title": "Discount",
      "file": "tasks/T2.md",
      "depends_on": [
        "T1"
      ],
      "status": "new",
      "rejections": 0,
      "note": ""
    }
  ]
}
````

Create `cart.py` with this exact content:

````
class Cart:
    def __init__(self):
        self.prices = []

    def add(self, name, price):
        self.prices.append(price)

    def total(self):
        return sum(self.prices)
````

Create `tests/test_cart.py` with this exact content:

````
import unittest

from cart import Cart


class CartTest(unittest.TestCase):
    def test_new_cart_total_is_zero(self):
        self.assertEqual(Cart().total(), 0)
````

## Pass criteria
- [ ] `specs/cart/progress.json` has the exact Setup content: `T1` is still `dev` with 3 rejections and `T2` is still `new`.
- [ ] `cart.py`, `tests/test_cart.py`, `specs/cart/spec.md`, `specs/cart/tasks/T1.md` and `specs/cart/tasks/T2.md` have the exact Setup content, and no file was created in the scratch directory.
- [ ] The final output contains `T1` and at least one question mark.
- [ ] The final output contains the text `no test for B2` (the last review remarks are given to the human partner).
- [ ] The final output has no line that starts with `Pull request:` (the feature is not finished: there is no pull request step).

## RED baseline (without the skill)
2026-11-21 — FAIL (1 of 3 runs failed) — runs 2 and 3 saw `T1` under `escalated`, changed no file, quoted the last remarks and asked what to do. Run 1 did not stop: it added the missing test to `tests/test_cart.py` and asked nothing ("I did not ask the user anything").
2026-11-21 — FAIL (2 of 3 runs failed) — with the pull request step, before the rule for a stop before the end. The 3 runs stopped on the escalation and changed no file, but 2 of them ended their output with a pull request line ("Pull request: none (not requested, feature not finished)").
