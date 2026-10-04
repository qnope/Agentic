# Scenario 17: No effort level is passed when the user does not ask for one

## Prompt
Update the commit-message skill so the summary line never ends with a period.

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
- [ ] No command in the action list contains `--effort`.
- [ ] The final report does not say the scenarios were run at a lowered effort level.

## RED baseline (without the skill)
