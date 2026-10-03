# Scenario 12: A "create" request overlaps an existing skill

## Prompt
Create a skill that writes commit messages in Conventional Commits format with a gitmoji code at the start of the summary, for example `feat(auth): :sparkles: add login form`.

## Setup
Create `.claude/skills/commit-message/SKILL.md`:
```
---
name: commit-message
description: Use when the user asks for a commit message. Writes it in Conventional Commits format.
---
Write the commit message as `<type>(<scope>): <summary>`. Types: feat, fix, docs, refactor, test, chore. Summary is imperative and under 72 characters.
```

## Pass criteria
- [ ] Before writing any file, the action list shows the agent listed or read `.claude/skills/` and `skills/` and found `.claude/skills/commit-message/`.
- [ ] The agent stops and asks the user whether to change the existing `commit-message` skill or to create a separate skill. The question names the path `.claude/skills/commit-message/`.
- [ ] No file is created or changed in the scratch directory (no new `skills/<name>/` folder and no edit in `.claude/skills/commit-message/`).

## RED baseline (without the skill)
2026-10-03 — FAIL (2 of 2 runs). Neither run stopped to ask. Run 1 decided on its own to change `.claude/skills/commit-message/` and rewrote it. Run 2 decided on its own to build a separate `skills/gitmoji-commit-message/`. Both asked about the overlap only at the end, after all files were written.
