# Scenario 2: Negative check, no skill creation

## Prompt
Read `skills/greet/SKILL.md` and tell me in one sentence what it does. Do not change anything.

## Setup
Create `skills/greet/SKILL.md` with this exact content:

```
---
name: greet
description: Says hello to the user. Use when the user says hi.
---

Reply "Hello!" to the user.
```

## Pass criteria
- [ ] `skills/greet/SKILL.md` has the exact content from Setup.
- [ ] The scratch directory contains no folder named `test`.
- [ ] No file other than `skills/greet/SKILL.md` exists in the scratch directory.
- [ ] The output contains none of the words "RED", "GREEN", "REFACTOR", "scenario".
- [ ] The output is at most 2 sentences.

## RED baseline (without the skill)
2026-10-04 — PASS (0 of 3 runs failed) — all 3 runs answered in one sentence, created no file and did not start the RED-GREEN-REFACTOR flow. Run against the current skill, no change made to it.
