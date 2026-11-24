# Scenario 5: Negative check, a behavior above 60 minutes is not planned

## Prompt
Plan the feature `report`.

## Setup
Copy `mcp-servers/tdd-progress/progress.py` from the repository to the same path in the scratch directory.

Create `specs/report/spec.md` with this exact content:

````
# Spec: report

Status: approved

## Goal
Add a module `report.py`. It computes the total of the sales and builds a PDF report of the sales for the managers.

## Behaviors
- B1: given `total([])`, the result is `0`.
- B2: given `total([10, 20])`, the result is `30`.
- B3: given a folder of CSV sales files, the result of `build_report(folder)` is a PDF file, sent by email to each manager listed in `managers.csv`: a cover page with the total of the year, then one page per month with a bar chart of the sales per product and a table of the 10 best customers.

## Out of scope
- None

## Test command
`python3 -m unittest discover -s tests`
````

## Pass criteria
- [ ] `specs/report/progress.json` does not exist and `specs/report/tasks` does not exist.
- [ ] `specs/report/spec.md` has the exact Setup content.
- [ ] The scratch directory contains no file other than `specs/report/spec.md` and `mcp-servers/tdd-progress/progress.py`.
- [ ] The final output contains the text `B3`, the text `60 minutes` and the text `split`. It does not contain the text `10 minutes` (the limit of a task is 60 minutes, no longer 10).

## RED baseline (without the skill)
2026-11-24 — FAIL (3 of 3 runs failed) — with the skill as it was before the 60 minutes limit. The 3 runs wrote no file and asked to split `B3`, but with the old limit: "A task is 10 minutes at most". 2 runs did not name 60 minutes. With the first criterion (no check of `10 minutes`), the third run passed because it wrote "about 60 minutes or more": the criterion was made harder.
