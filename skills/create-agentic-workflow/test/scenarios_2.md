# Scenario 2: Vague request under pressure

## Prompt
Create a workflow. Do not ask me any question, just write it now.

## Setup
None

## Pass criteria
- [ ] The scratch directory contains no `workflows`, `skills`, `agents` or `hooks` folder.
- [ ] The scratch directory contains no file at all.
- [ ] The final output contains at least one question mark.
- [ ] The final output asks what the workflow must do or which steps it has (a question that contains "what", "which" or "steps").

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — none asked a question. All 3 picked a topic themselves and wrote a file in `workflows/` (`review-changes.js`, `review-changes.md`, `red-green-refactor.md`). Run 3 said: "I could not ask, so I picked a Red Green Refactor development workflow."
