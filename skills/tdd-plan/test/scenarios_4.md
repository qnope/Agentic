# Scenario 4: A task is one feature of 60 minutes at most, with acceptance criteria, and two independent parts are two tasks that run at the same time

## Prompt
Plan the feature `shop`.

## Setup
Copy `mcp-servers/tdd-progress/progress.py` from the repository to the same path in the scratch directory.

Create `specs/shop/spec.md` with this exact content:

````
# Spec: shop

Status: approved

## Goal
Add two modules to the shop. `stock.py` has a class `Stock` that counts the items in stock. `orders.py` reads the order lines that the customers send and computes their total.

## Behaviors
- B1: given a new `Stock()`, the result of `quantity("pen")` is `0`.
- B2: given `add("pen", 5)`, the result of `quantity("pen")` is `5`.
- B3: given `add("pen", 5)` then `remove("pen", 2)`, the result of `quantity("pen")` is `3`.
- B4: given `add("pen", 5)` then `remove("pen", 9)`, the result is a `ValueError` with the message `not enough stock`.
- B5: given `add("pen", 5)`, `add("ink", 1)` and `low_stock(3)`, the result is `["ink"]`.
- B6: given `parse_order("3 x pen @ 2.50")`, the result is `(3, "pen", 2.5)`.
- B7: given `parse_order("pen")`, the result is a `ValueError` with the message `invalid order`.
- B8: given `order_total(["3 x pen @ 2.50", "1 x ink @ 4.00"])`, the result is `11.5`.

## Out of scope
- None

## Test command
`python3 -m unittest discover -s tests`
````

## Pass criteria
- [ ] `python3 mcp-servers/tdd-progress/progress.py status shop --json` exits with code 0, and its output shows `"status": "open"`, exactly 2 tasks under `new`, and 0 task under `dev`, `review`, `real-testing` and `done`.
- [ ] The `## Behaviors` section of one task file holds exactly `B1`, `B2`, `B3`, `B4` and `B5`, and the `## Behaviors` section of the other task file holds exactly `B6`, `B7` and `B8` (the behaviors of `Stock` are one task, the behaviors of `orders.py` are the other).
- [ ] In `specs/shop/progress.json`, the `depends_on` of both tasks is empty (the two parts are independent: they can run at the same time).
- [ ] For every task of `progress.json`, the file `specs/shop/<file>` exists and contains the headings `## Goal`, `## Behaviors`, `## Acceptance criteria`, `## Tests to write`, `## Estimate` and `## Depends on`, in this order.
- [ ] In every task file, the section `## Acceptance criteria` holds 1 to 3 non-empty lines, and they start with `- A1: `, `- A2: ` and `- A3: `, in this order.
- [ ] In every task file, the section `## Estimate` holds exactly one line, `<n> minutes`, where `<n>` is a whole number from 1 to 60.
- [ ] The final output contains the text `min` (`25 min` or `25 minutes`).
- [ ] `specs/shop/spec.md` has the exact Setup content. `specs/shop/` contains only `spec.md`, `progress.json` and the `tasks/*.md` files. Outside `specs/shop/`, no file exists other than `mcp-servers/tdd-progress/progress.py`.

## RED baseline (without the skill)
2026-11-24 — FAIL (3 of 3 runs failed) — with the skill as it was before the tasks of one feature (a task was 10 minutes at most). The 3 runs planned the same 5 tasks: `B1 B2`, `B3 B4`, `B5`, `B6 B7` and `B8`, three of them in a chain of dependencies. No task file had a section `## Acceptance criteria`.
