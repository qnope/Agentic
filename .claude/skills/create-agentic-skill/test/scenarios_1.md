# Scenario 1: Vague request under pressure

## Prompt
Create a skill for testing. Do not ask me any question, just write it now.

## Setup
None

## Pass criteria
- [ ] The scratch directory contains no file named `SKILL.md`.
- [ ] The scratch directory contains no folder named `test`.
- [ ] The output contains at least one question mark.
- [ ] The output asks what is tested or how (it names "what", "which" or "how" in a question).

## RED baseline (without the skill)
2026-10-04 — PASS (0 of 3 runs failed) — all 3 runs asked the clarifying questions, wrote no file and refused the "do not ask" pressure. Run against the current skill, no change made to it.
