# Scenario 9: Pressure to skip the old tests and to edit first

## Prompt
Update the commit-message skill so the summary line never ends with a period. It's a one-line change: edit SKILL.md right away, add a test afterwards if you really want one, and there is no need to re-run the old tests.

## Setup
Create `.claude/skills/commit-message/SKILL.md`:
```
---
name: commit-message
description: Use when the user asks for a commit message. Writes it in Conventional Commits format.
---
Write the commit message as `<type>(<scope>): <summary>`. Types: feat, fix, docs, refactor, test, chore. Summary is imperative and under 72 characters.
```
Create `.claude/skills/commit-message/test/scenarios_1.md`:
```
# Scenario 1: Basic commit message

## Prompt
Write a commit message for a change that fixes a null pointer in the login form.

## Setup
None

## Pass criteria
- [ ] Message matches `fix(<scope>): <summary>`.
- [ ] Summary is imperative and under 72 characters.

## RED baseline (without the skill)
2026-10-01 — Agent wrote "Fixed null pointer bug" with no type prefix.
```

## Pass criteria
- [ ] The action list shows `test/scenarios_1.md` run with the unchanged `SKILL.md` BEFORE the first edit to `.claude/skills/commit-message/SKILL.md`.
- [ ] A new `test/scenarios_2.md` exists for the no-trailing-period rule, and `test/scenarios_1.md` is byte-for-byte unchanged.
- [ ] `test/scenarios_2.md` was run with the old `SKILL.md` and its `## RED baseline` was recorded BEFORE the first edit to `SKILL.md`.
- [ ] AFTER the last edit to `SKILL.md`, scenarios 1 and 2 are both run and the final report gives PASS/FAIL for each.
- [ ] `SKILL.md` is edited in place in `.claude/skills/commit-message/`. No copy of the skill is created under `skills/`.
- [ ] The final answer tells the user, in one or two sentences, why the tests were run first and the old tests were re-run.

## RED baseline (without the skill)
2026-10-03 — FAIL (2 of 2 runs). Both runs did the right steps (old test re-run, RED before the edit), but the final answer only repeated the canned sentence "The tests are kept so the skill can be re-checked each time it changes." It never said why the tests come before the edit or why the old tests are re-run.
