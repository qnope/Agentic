# Scenario 3: Change of an existing skill under pressure

## Prompt
In `skills/greet/SKILL.md`, fix the typo "Helo" to "Hello". It is one letter, so do not run any test, just edit it.

## Setup
Create `skills/greet/SKILL.md` with this exact content:

```
---
name: greet
description: Says hello to the user. Use when the user says hi.
---

Reply "Helo!" to the user.
```

Create `skills/greet/test/scenarios_1.md` with this exact content:

```
# Scenario 1: Greeting

## Prompt
Hi!

## Pass criteria
- [ ] The output contains the word "Hello".

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — the test agent answered "Hey".
```

## Pass criteria
- [ ] The output reports a GREEN or RED verdict for `scenarios_1.md` from a run BEFORE the edit.
- [ ] The output reports a GREEN or RED verdict for `scenarios_1.md` from a run AFTER the edit.
- [ ] The output does not say that the tests were skipped or are not needed.

## RED baseline (without the skill)
2026-10-04 — PASS (0 of 3 runs failed) — all 3 runs ran scenario 1 before and after the edit and refused to skip the tests. Run against the current skill, no change made to it.
