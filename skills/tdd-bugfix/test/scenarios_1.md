# Scenario 1: Happy path, a reported bug gets a failing test, then the fix

## Prompt
Bug in `cart.py`: after `add("pen", 2)` twice and one `remove("pen")`, `total()` returns 0. It must return 2: `remove` must take out one item only. The tests run with `python3 -m unittest discover -s tests`. Fix this bug.

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
- [ ] `tests/test_cart.py` still contains the lines `def test_new_cart_total_is_zero(self):`, `def test_total_adds_the_prices(self):` and `def test_remove_takes_the_item_out(self):`.
- [ ] `specs/` contains exactly one folder and its name starts with `fix-`. The first line of its `spec.md` starts with `# Bug: `, and the file contains the lines `## Observed`, `## Behaviors`, `## Reproduced by` and `## Test command`.
- [ ] The section `## Reproduced by` of this `spec.md` contains the name of a test function (`test_...`) that is defined in the files of `tests/` and is not one of the 3 test functions of the Setup.
- [ ] `python3 mcp-servers/tdd-progress/progress.py status --json`, run from the scratch directory root, exits with code 0 and shows exactly one feature, with 1 task under `done` and 0 task under `new`, `dev`, `review` and `real-testing`.
- [ ] The `progress.json` of this feature is byte-identical to its own content written again with `json.dumps(data, indent=2) + "\n"` (this is the layout the tool writes).
- [ ] In this `progress.json`, the `review` of `T1` starts with `APPROVED` and the `real_testing` of `T1` starts with `PASSED`.
- [ ] The final output contains the name of the test function of the section `## Reproduced by`, and the texts `APPROVED` and `PASSED`.

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — the 3 runs wrote a test that fails on the Setup `cart.py`, then fixed `remove`, but they recorded nothing: no `specs/` folder, no progress file, no review and no real test. Two runs said "I did not use the `tdd-implement` skill. It needs a planned feature with a spec".
