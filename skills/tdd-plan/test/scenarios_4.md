# Scenario 4: Every task is 10 minutes at most for the human partner

## Prompt
Plan the feature `library`.

## Setup
Copy `mcp-servers/tdd-progress/progress.py` from the repository to the same path in the scratch directory.

Create `specs/library/spec.md` with this exact content:

````
# Spec: library

Status: approved

## Goal
Add a class `Library` to `library.py`. It holds books, lends them to members and computes late fees.

## Behaviors
- B1: given a new `Library()`, the result of `books()` is `[]`.
- B2: given `add_book("Dune")` then `add_book("Emma")`, the result of `books()` is `["Dune", "Emma"]`.
- B3: given `add_book("Dune")` twice, the result of the second call is a `ValueError` with the message `duplicate book`.
- B4: given the book `"Dune"` and `lend("Dune", "ann")`, the result of `borrower("Dune")` is `"ann"`.
- B5: given the book `"Dune"` lent to `"ann"` and `lend("Dune", "bob")`, the result is a `ValueError` with the message `already lent`.
- B6: given the book `"Dune"` lent to `"ann"` and `give_back("Dune")`, the result of `borrower("Dune")` is `None`.
- B7: given `late_fee(14)`, the result is `0`.
- B8: given `late_fee(20)`, the result is `3.0`: `0.5` per day after day `14`.
- B9: given the books `"Dune"` and `"Emma"` and `search("u")`, the result is `["Dune"]`.
- B10: given `search("")`, the result is a `ValueError` with the message `empty query`.

## Out of scope
- None

## Test command
`python3 -m unittest discover -s tests`
````

## Pass criteria
- [ ] `python3 mcp-servers/tdd-progress/progress.py status library --json` exits with code 0, and its output shows `"status": "open"`, at least 3 tasks under `new`, and 0 task under `dev`, `review`, `real-testing` and `done`.
- [ ] For every task of `progress.json`, the file `specs/library/<file>` exists and contains the headings `## Goal`, `## Behaviors`, `## Tests to write`, `## Estimate` and `## Depends on`, in this order.
- [ ] In every task file, the section `## Estimate` holds exactly one line, `<n> minutes`, where `<n>` is a whole number from 1 to 10.
- [ ] Each of `B1` to `B10` appears in the `## Behaviors` section of exactly one task file.
- [ ] The final output contains the text `min` (`8 min` or `8 minutes`).
- [ ] `specs/library/spec.md` has the exact Setup content. `specs/library/` contains only `spec.md`, `progress.json` and the `tasks/*.md` files. Outside `specs/library/`, no file exists other than `mcp-servers/tdd-progress/progress.py`.

## RED baseline (without the skill)
2026-11-22 — FAIL (3 of 3 runs failed) — with the skill as it was before the 10 minutes limit. The 3 runs planned the feature (7, 4 and 4 tasks), but no task was sized: no task file had a section `## Estimate` and no output gave a time. In 2 runs, two tasks held 3 behaviors each (`B1` to `B3`, `B4` to `B6`).
