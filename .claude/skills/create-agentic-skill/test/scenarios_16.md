# Scenario 16: The user asks for the test runs at low effort

## Prompt
Update the commit-message skill so the summary line never ends with a period. Run the tests at low effort to save money. At low effort, one run per scenario is enough.

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
- [ ] Every RED, GREEN and REFACTOR run in the action list is a `claude -p` command that contains `--effort low`. No run is launched with a subagent tool.
- [ ] In the final run after the last edit to `SKILL.md`, the action list shows each scenario run at least 3 times, each in its own fresh scratch directory.
- [ ] The final report says the scenarios were run at effort `low`.
- [ ] The final answer tells the user, in one or two sentences, why each scenario was still run 3 times.

## RED baseline (without the skill)
