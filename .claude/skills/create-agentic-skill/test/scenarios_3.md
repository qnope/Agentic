# Scenario 3: Modify an existing skill

## Prompt
Update the commit-message skill so it also adds a `Refs: <TICKET>` footer when the current git branch name contains a ticket ID like `ABC-123`.

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
- [ ] Re-runs the existing `test/scenarios_1.md` before editing `SKILL.md`.
- [ ] Adds a new file `test/scenarios_2.md` (next free number) and does not overwrite `test/scenarios_1.md`.
- [ ] Runs the new scenario without the change (RED) and records the failure before editing `SKILL.md`.
- [ ] After editing `SKILL.md`, runs ALL scenarios (1 and 2) and reports PASS/FAIL for each.

## RED baseline (without the skill)
2026-10-03 — FAIL (2 of 4 criteria failed). Passed: it added `test/scenarios_2.md` without overwriting scenario 1, and ran a RED baseline before editing. Failed: it did not re-run `test/scenarios_1.md` before editing `SKILL.md`, and after the edit it ran only scenario 2: "Scenario 1 is unaffected ... I did not re-run it."
