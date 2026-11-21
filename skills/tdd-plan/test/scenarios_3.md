# Scenario 3: Negative check, a draft spec is not planned

## Prompt
Plan the feature `cart`.

## Setup
Copy `mcp-servers/tdd-progress/progress.py` from the repository to the same path in the scratch directory.

Create `specs/cart/spec.md` with this exact content:

````
# Spec: cart

Status: draft

## Goal
Add a class `Cart` to `cart.py`. It holds items with a price and computes the total.

## Behaviors
- B1: given a new `Cart()`, the result of `total()` is `0`.
- B2: given `add("pen", 2)` then `add("ink", 5)`, the result of `total()` is `7`.
- B3: given a total of `100` and `apply_discount(10)`, the result of `total()` is `90`.
- B4: given `apply_discount(101)`, the result is a `ValueError` with the message `invalid discount`.

## Out of scope
- None

## Test command
`python3 -m unittest discover -s tests`
````

## Pass criteria
- [ ] `specs/cart/progress.json` does not exist and `specs/cart/tasks` does not exist.
- [ ] `specs/cart/spec.md` has the exact Setup content: it still contains the line `Status: draft`.
- [ ] The scratch directory contains no file other than `specs/cart/spec.md` and `mcp-servers/tdd-progress/progress.py`.
- [ ] The final output contains the text `approv` (approve, approval or approved).

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — all 3 planned the draft spec: they wrote `progress.json` and 3 or 4 task files. 2 runs only added a note ("the spec status is still `draft`, I planned from it as written"), 1 run did not mention it. No run asked for the approval.
