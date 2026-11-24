# Scenario 1: Happy path in a git repository, two dependent tasks go from new to done with one cycle per behavior, then the pull request

## Prompt
Implement the feature `cart`.

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

## Acceptance criteria
- A1: a new `Cart()`, then `add("pen", 2)` and `add("ink", 5)`: `total()` is `0` before the first `add` and `7` after the second.

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

## Acceptance criteria
- A1: `add("box", 100)`, `apply_discount(10)`, then `apply_discount(101)`: `total()` is `90` after the first discount, and the second discount is a `ValueError` with the message `invalid discount`.

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

Create `.gitignore` with this exact content:

````
/origin.git/
__pycache__/
````

Then make the scratch directory a git repository on the branch `main`, with every Setup file in one commit and a local folder as the remote `origin`. Run these commands from the scratch directory root, in this order:

````
git init --quiet --bare --initial-branch=main origin.git
git init --quiet --initial-branch=main
git config user.name "Scenario"
git config user.email "scenario@example.com"
git add --all
git commit --quiet --message "initial"
git remote add origin "$PWD/origin.git"
git push --quiet origin main
````

## Pass criteria
- [ ] `git status --porcelain`, run from the scratch directory root before any other check, prints nothing (every file of the feature is committed).
- [ ] `git log --format=%s feature/cart`, run from the scratch directory root, prints exactly these 4 lines in this order: `cart: closed`, `cart T2: Discount`, `cart T1: Cart total`, `initial` (one commit per task, with its id, then the end of the feature).
- [ ] `git --git-dir=origin.git log --format=%s feature/cart`, run from the scratch directory root, prints the same 4 lines (the branch of the feature is pushed).
- [ ] `git log --format=%s main` and `git --git-dir=origin.git log --format=%s main`, run from the scratch directory root, each print only the line `initial` (nothing is committed on the default branch).
- [ ] The final output has a line that starts with `Pull request: none (` and contains `feature/cart` (the remote is a local folder: no pull request can be opened there, and the output says so).
- [ ] The final output contains no `https://` link (no pull request link is invented).
- [ ] `python3 mcp-servers/tdd-progress/progress.py status cart` exits with code 0 and its output shows 2 tasks under `done` and 0 task under `new`, `dev`, `review` and `real-testing`.
- [ ] `specs/cart/progress.json` is byte-identical to its own content written again with `json.dumps(data, indent=2) + "\n"` (this is the layout the tool writes).
- [ ] `python3 -m unittest discover -s tests`, run from the scratch directory root, exits with code 0 and prints `Ran <n> tests` with n at least 4.
- [ ] The files in `tests/` contain the texts `total`, `apply_discount` and `invalid discount`.
- [ ] `python3 -c "from cart import Cart; c = Cart(); c.add('box', 100); c.apply_discount(10); assert c.total() == 90"`, run from the scratch directory root, exits with code 0.
- [ ] `specs/cart/spec.md`, `specs/cart/tasks/T1.md` and `specs/cart/tasks/T2.md` have the exact Setup content.
- [ ] The final output has a line that contains `T1`, `APPROVED` and `PASSED`, and a line that contains `T2`, `APPROVED` and `PASSED`.
- [ ] In `specs/cart/progress.json`, the `review` of `T1` and the `review` of `T2` each start with `APPROVED` and each contain at least 2 names of test functions (`test_...`) that are defined in the files of `tests/` (the reviewer output is recorded; the same name twice counts twice).
- [ ] In `specs/cart/progress.json`, the `real_testing` of `T1` starts with `PASSED` and contains `B1`, `B2` and `A1`, and the `real_testing` of `T2` starts with `PASSED` and contains `B3`, `B4` and `A1` (the real tester output is recorded, and it checks the acceptance criteria).
- [ ] In the run report, which quotes every output of the agents, the first output of the developer for `T1` has a line that starts with `B1:` and a line that starts with `B2:`, and the first output of the developer for `T2` has a line that starts with `B3:` and a line that starts with `B4:`. Each of these 4 lines contains `RED` and `GREEN` (one Red-Green-Refactor cycle per behavior).
- [ ] The folders `specs/cart/real-testing/T1/` and `specs/cart/real-testing/T2/` each contain at least one file (what the real tester used or saw).

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — the 3 runs wrote the 4 tests then the code in one pass, but never used the progress tool or the agents: both tasks stayed `new`, with no review and no real test ("There was no independent review and no real-user test").
2026-11-21 — FAIL (3 of 3 runs failed) — with the skill as it was before the pull request step. Runs 1 and 3 finished both tasks, and the tool made one commit per task on `feature/cart`. But the feature was not closed, the branch was not pushed and the output had no line `Pull request:`. Run 2 finished no task: the permission system of the test session stopped it when it recorded its own review.
2026-11-24 — FAIL (3 of 3 runs failed) — with the agents as they were before the cycle per behavior and the acceptance criteria. The 3 runs finished both tasks and passed the 15 other criteria. Each output of the developer had one `RED:` line for the whole task ("RED: 2 new tests failed"), not one line per behavior. No output of the real tester named `A1`.
