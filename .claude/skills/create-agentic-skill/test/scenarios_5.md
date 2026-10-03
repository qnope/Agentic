# Scenario 5: New skills go in `skills/`

## Prompt
Create a skill that turns a bullet list of release notes into a CHANGELOG.md entry.

## Setup
None

## Pass criteria
- [ ] The new skill is created at `<project root>/skills/<skill-name>/SKILL.md`, with its tests in `<project root>/skills/<skill-name>/test/`.
- [ ] Nothing is created under `<project root>/.claude/skills/`.
- [ ] The final report tells the user the skill is in `skills/`.

## RED baseline (without the skill)
2026-10-03 — FAIL. The agent followed the skill as it was and created `.claude/skills/release-notes-to-changelog/` (SKILL.md and test/). Nothing was created under `skills/`.
