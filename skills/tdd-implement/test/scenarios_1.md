# Scenario 1: Happy path, two dependent tasks go from new to done

## Prompt
Implement the feature `cart`.

## Setup
Copy `mcp-servers/tdd-progress/progress.py` from the repository to the same path in the scratch directory.

Copy `agents/tdd-developer.md` from the repository to the same path in the scratch directory.

Copy `agents/tdd-reviewer.md` from the repository to the same path in the scratch directory.

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
      "status": "new",
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

## Pass criteria
- [ ] `python3 mcp-servers/tdd-progress/progress.py status cart` exits with code 0 and its output shows 2 tasks under `done` and 0 task under `new`, `dev` and `review`.
- [ ] `specs/cart/progress.json` is byte-identical to its own content written again with `json.dumps(data, indent=2) + "\n"` (this is the layout the tool writes).
- [ ] `python3 -m unittest discover -s tests`, run from the scratch directory root, exits with code 0 and prints `Ran <n> tests` with n at least 4.
- [ ] The files in `tests/` contain the texts `total`, `apply_discount` and `invalid discount`.
- [ ] `python3 -c "from cart import Cart; c = Cart(); c.add('box', 100); c.apply_discount(10); assert c.total() == 90"`, run from the scratch directory root, exits with code 0.
- [ ] `specs/cart/spec.md`, `specs/cart/tasks/T1.md` and `specs/cart/tasks/T2.md` have the exact Setup content.
- [ ] The final output has a line that contains `T1` and `APPROVED`, and a line that contains `T2` and `APPROVED`.
- [ ] In `specs/cart/progress.json`, the `note` of `T1` and the `note` of `T2` each start with `APPROVED` and each contain at least 2 names of test functions (`test_...`) that are defined in the files of `tests/` (the reviewer output is recorded; the same name twice counts twice).

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — run 1 wrote 4 tests and the code but never used the progress tool: both tasks stayed `new` and there was no review. Runs 2 and 3 moved both tasks to `done` with `progress.py` and gave it an `APPROVED` note, because the tool refuses `done` without one, but their final output gave no verdict per task ("The reviews were not independent").
