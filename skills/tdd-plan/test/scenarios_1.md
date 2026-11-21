# Scenario 1: Happy path, an approved spec becomes tasks and a progress file

## Prompt
Plan the feature `cart`.

## Setup
Copy `mcp-servers/tdd-progress/progress.py` from the repository to the same path in the scratch directory.

Create `specs/cart/spec.md` with this exact content:

````
# Spec: cart

Status: approved

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
- [ ] `python3 mcp-servers/tdd-progress/progress.py status cart` exits with code 0, and its output shows `"status": "open"`, at least 2 tasks under `new`, and 0 task under `dev`, `review` and `done`.
- [ ] `specs/cart/progress.json` is byte-identical to its own content written again with `json.dumps(data, indent=2) + "\n"`, and every task in it has exactly the keys `id`, `title`, `file`, `depends_on`, `status`, `rejections` and `note` (this is the layout the tool writes).
- [ ] In `specs/cart/progress.json`, `test_command` is exactly `python3 -m unittest discover -s tests`.
- [ ] For every task of `progress.json`, the file `specs/cart/<file>` exists and contains the headings `## Goal`, `## Behaviors`, `## Tests to write` and `## Depends on`, in this order.
- [ ] Each of `B1`, `B2`, `B3` and `B4` appears in the `## Behaviors` section of exactly one task file.
- [ ] The task that holds `B3` is the task that holds `B2`, or depends on it in `progress.json` (directly or through other tasks).
- [ ] In each task file, the task ids (`T<number>`) named in the `## Depends on` section are exactly the ids of its `depends_on` in `progress.json`.
- [ ] `specs/cart/spec.md` has the exact Setup content. `specs/cart/` contains only `spec.md`, `progress.json` and the `tasks/*.md` files. Outside `specs/cart/`, no file exists other than `mcp-servers/tdd-progress/progress.py` (no code, no test and no temporary file were written).
- [ ] The final output contains the text `tdd-implement`.

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — all 3 found `progress.py` in the project and created `progress.json` with it, so the 3 tool criteria passed. All 3 failed on the task files: each run invented its own layout (Red/Green/Refactor steps, no `## Behaviors`, `## Tests to write` or `## Depends on` heading), so no behavior could be matched to a task. No run named the next step `tdd-implement`.
