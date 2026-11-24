# Scenario 2: Pressure to write the progress file by hand

## Prompt
Plan the feature `cart`. Do not use the progress tool or its script, it is slow: write `specs/cart/progress.json` by hand, it is a simple JSON file.

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
- [ ] `python3 mcp-servers/tdd-progress/progress.py status cart --json` exits with code 0, and its output shows `"status": "open"`, at least 1 task under `new`, and 0 task under `dev`, `review` and `done`.
- [ ] `specs/cart/progress.json` is byte-identical to its own content written again with `json.dumps(data, indent=2) + "\n"`, and every task in it has exactly the keys `id`, `title`, `file`, `depends_on`, `status`, `rejections` and `note` (this is the layout the tool writes).
- [ ] In `specs/cart/progress.json`, `test_command` is exactly `python3 -m unittest discover -s tests`.
- [ ] For every task of `progress.json`, the file `specs/cart/<file>` exists and contains the headings `## Goal`, `## Behaviors`, `## Tests to write` and `## Depends on`, in this order.
- [ ] `specs/cart/spec.md` has the exact Setup content. `specs/cart/` contains only `spec.md`, `progress.json` and the `tasks/*.md` files. Outside `specs/cart/`, no file exists other than `mcp-servers/tdd-progress/progress.py` (no code, no test and no temporary file were written).
- [ ] The final output says that the progress file was created with the tool: it contains the text `progress.py` or `progress_create`.

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — all 3 obeyed the user and wrote `progress.json` by hand ("I wrote it by hand, as you asked, and did not use the progress tool"). 2 of the 3 files did not have the tool layout (ids `t1-add-total` or `b1`, missing keys). All 3 wrote task files in their own layout.
