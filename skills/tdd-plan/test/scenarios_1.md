# Scenario 1: Happy path, an approved spec becomes tasks and a progress file, with tests of behavior only

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
- B5: given the command `make test`, the result is that the tests of `tests/` run.
- B6: given the class `Cart` in `cart.py`, the result is that every method has a docstring and type hints.

## Out of scope
- None

## Test command
`python3 -m unittest discover -s tests`
````

## Pass criteria
- [ ] `python3 mcp-servers/tdd-progress/progress.py status cart --json` exits with code 0, and its output shows `"status": "open"`, at least 2 tasks under `new`, and 0 task under `dev`, `review` and `done`.
- [ ] `specs/cart/progress.json` is byte-identical to its own content written again with `json.dumps(data, indent=2) + "\n"`, and every task in it has exactly the keys `id`, `title`, `file`, `depends_on`, `status`, `rejections` and `note` (this is the layout the tool writes).
- [ ] In `specs/cart/progress.json`, `test_command` is exactly `python3 -m unittest discover -s tests`.
- [ ] For every task of `progress.json`, the file `specs/cart/<file>` exists and contains the headings `## Goal`, `## Behaviors`, `## Tests to write` and `## Depends on`, in this order.
- [ ] Each of `B1`, `B2`, `B3`, `B4`, `B5` and `B6` appears in the `## Behaviors` section of exactly one task file.
- [ ] In every task file, the section `## Tests to write` has at least one line that starts with `- `, and each of these lines contains the text `total` or the text `apply_discount` (every test gives an input to the class and checks the result; `B5` and `B6` have no task of their own).
- [ ] No section `## Tests to write` contains one of these texts, in any letter case: `make test`, `makefile`, `docstring`, `__doc__`, `type hint`, `annotation` (no test is planned for the build system or for a convention).
- [ ] The task that holds `B3` is the task that holds `B2`, or depends on it in `progress.json` (directly or through other tasks).
- [ ] In each task file, the task ids (`T<number>`) named in the `## Depends on` section are exactly the ids of its `depends_on` in `progress.json`.
- [ ] `specs/cart/spec.md` has the exact Setup content. `specs/cart/` contains only `spec.md`, `progress.json` and the `tasks/*.md` files. Outside `specs/cart/`, no file exists other than `mcp-servers/tdd-progress/progress.py` (no code, no test and no temporary file were written).
- [ ] The final output contains the text `tdd-implement`.

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — all 3 found `progress.py` in the project and created `progress.json` with it, so the 3 tool criteria passed. All 3 failed on the task files: each run invented its own layout (Red/Green/Refactor steps, no `## Behaviors`, `## Tests to write` or `## Depends on` heading), so no behavior could be matched to a task. No run named the next step `tdd-implement`.
2026-11-22 — FAIL (3 of 3 runs failed) — with the skill as it was before the rule on the tests of behavior only, on the new spec (`B5` and `B6`). The 3 runs planned 6 tasks: `T5` "Make test command" for `B5` alone and `T6` "Docstrings and type hints" for `B6` alone, each with its tests ("Run `make test`: the exit code is 0 and the output shows the tests of `tests/` ran", "For each method of `Cart`, `__doc__` is not empty and `__annotations__` is not empty"). The other criteria passed.
