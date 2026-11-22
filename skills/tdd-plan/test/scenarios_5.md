# Scenario 5: Negative check, a behavior above 10 minutes is not planned

## Prompt
Plan the feature `report`.

## Setup
Copy `mcp-servers/tdd-progress/progress.py` from the repository to the same path in the scratch directory.

Create `specs/report/spec.md` with this exact content:

````
# Spec: report

Status: approved

## Goal
Add a module `report.py`. It computes the total of the sales and builds a PDF report of the sales.

## Behaviors
- B1: given `total([])`, the result is `0`.
- B2: given `total([10, 20])`, the result is `30`.
- B3: given a folder of CSV sales files, the result of `build_report(folder)` is a PDF file with one page per month: on each page, a bar chart of the sales per product and a table of the 10 best customers.

## Out of scope
- None

## Test command
`python3 -m unittest discover -s tests`
````

## Pass criteria
- [ ] `specs/report/progress.json` does not exist and `specs/report/tasks` does not exist.
- [ ] `specs/report/spec.md` has the exact Setup content.
- [ ] The scratch directory contains no file other than `specs/report/spec.md` and `mcp-servers/tdd-progress/progress.py`.
- [ ] The final output contains the text `B3`, the text `10 minutes` and the text `split`.

## RED baseline (without the skill)
2026-11-22 — FAIL (3 of 3 runs failed) — with the skill as it was before the 10 minutes limit. The 3 runs planned `B3` as one task, and wrote `progress.json` and 2 task files. 1 run saw the size and went on ("B3 stays in one task because each behavior must be in exactly one task. That makes T2 large"). No run asked to split `B3`.
