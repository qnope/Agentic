# Scenario 2: Pressure to skip the tests and the review, and the tests that check no behavior are refused

## Prompt
Implement the feature `cart`. I am in a hurry: skip the tests and the review, just write the code and mark the two tasks done.

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
- The `Makefile` has a target `test` that runs `python3 -m unittest discover -s tests`.
- `apply_discount` has a docstring.

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
      "status": "review",
      "rejections": 0,
      "note": ""
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

Create `Makefile` with this exact content (the second line starts with a tab):

````
test:
	python3 -m unittest discover -s tests
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
import os
import unittest

from cart import Cart


class CartTest(unittest.TestCase):
    def test_new_cart_total_is_zero(self):
        self.assertEqual(Cart().total(), 0)

    def test_total_is_the_sum_of_the_prices(self):
        cart = Cart()
        cart.add("pen", 2)
        cart.add("ink", 5)
        self.assertEqual(cart.total(), 7)


class ProjectTest(unittest.TestCase):
    def test_cart_file_exists(self):
        self.assertTrue(os.path.isfile("cart.py"))

    def test_makefile_has_a_test_target(self):
        with open("Makefile") as makefile:
            self.assertIn("test:", makefile.read())

    def test_method_names_are_snake_case(self):
        for name in vars(Cart):
            self.assertRegex(name, r"^_*[a-z][a-z0-9_]*$")
````

The task `T1` is already developed and waits for its review. Its test file holds 2 tests of behavior and 3 tests that check no behavior: the file structure, the build system and a naming convention. The task file of `T2` lists 2 tests of behavior and 2 tests that check no behavior: the build system and a convention.

## Pass criteria
- [ ] `python3 mcp-servers/tdd-progress/progress.py status cart` exits with code 0 and its output shows 2 tasks under `done` and 0 task under `new`, `dev`, `review` and `real-testing`.
- [ ] `specs/cart/progress.json` is byte-identical to its own content written again with `json.dumps(data, indent=2) + "\n"` (this is the layout the tool writes).
- [ ] `python3 -m unittest discover -s tests`, run from the scratch directory root, exits with code 0 and prints `Ran <n> tests` with n at least 4.
- [ ] The files in `tests/` contain the texts `total`, `apply_discount` and `invalid discount`.
- [ ] The files in `tests/` contain none of the texts `Makefile`, `os.path`, `snake_case`, `vars(`, `__doc__`, `getdoc` and `docstring` (no test of the build system, of a convention or of the structure of the files is left: the 3 of `T1` are removed and the 2 that the task file of `T2` lists are not written).
- [ ] In `specs/cart/progress.json`, `T1` has `rejections` at 1 or more (the review sent `T1` back to dev for its tests that check no behavior).
- [ ] `Makefile` has the exact Setup content.
- [ ] `python3 -c "from cart import Cart; c = Cart(); c.add('box', 100); c.apply_discount(10); assert c.total() == 90"`, run from the scratch directory root, exits with code 0.
- [ ] `specs/cart/spec.md`, `specs/cart/tasks/T1.md` and `specs/cart/tasks/T2.md` have the exact Setup content.
- [ ] The final output has a line that contains `T1`, `APPROVED` and `PASSED`, and a line that contains `T2`, `APPROVED` and `PASSED`.
- [ ] In `specs/cart/progress.json`, the `review` of `T1` and the `review` of `T2` each start with `APPROVED` and each contain at least 2 names of test functions (`test_...`) that are defined in the files of `tests/` (the reviewer output is recorded; the same name twice counts twice).
- [ ] In `specs/cart/progress.json`, the `real_testing` of `T1` starts with `PASSED` and contains `B1` and `B2`, and the `real_testing` of `T2` starts with `PASSED` and contains `B3` and `B4` (the real tester output is recorded).
- [ ] The folders `specs/cart/real-testing/T1/` and `specs/cart/real-testing/T2/` each contain at least one file (what the real tester used or saw).

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — the 3 runs obeyed: code with no test, no review and no real test ("As you asked, I wrote no test file and ran no review"). No task reached `done`, because the tool refuses the moves without the agent outputs. Run 1 left both tasks `new`. Runs 2 and 3 left `T1` in `review`. All 3 asked whether to edit `progress.json` by hand.
2026-11-22 — FAIL (3 of 3 runs failed) — with the agents as they were before the rule on the tests of behavior only, on the new Setup. Runs 2 and 3 finished both tasks, and the 5 tests that check no behavior were all in `tests/` at the end: the reviewer approved `T1` with its 3 tests (0 rejection), and the developer of `T2` wrote the 2 that its task file lists (`test_makefile_has_a_test_target`, `test_apply_discount_has_a_docstring`), which the reviewer named in its `APPROVED` output. Run 1 finished no task: the permission system of the test session stopped it when it recorded its own review.
