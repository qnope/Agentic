# Scenario 4: Negative check, not an agent request

## Prompt
Explain in at most 3 sentences what a subagent is and why someone would use one. Do not create or edit any file.

## Setup
None

## Pass criteria
- [ ] The scratch directory contains no file at all.
- [ ] The final output has at most 3 sentences of explanation.
- [ ] The final output does not contain the text `Use when`.

## RED baseline (without the skill)
2026-10-04 — PASS (0 of 3 runs failed) — all 3 gave a 3-sentence explanation and created no file. Expected for a negative check: it only has value in the GREEN runs, where it checks that the skill does not over-trigger.
