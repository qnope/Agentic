# Scenario 1: Basic creation

## Prompt
Create a skill that writes commit messages in Conventional Commits format.

## Setup
None

## Pass criteria
- [ ] Writes at least one `test/scenarios_<n>.md` file in the new skill folder BEFORE writing `SKILL.md`.
- [ ] Runs a baseline (RED) test without the new skill and records the result in each scenario file under `## RED baseline`.
- [ ] `SKILL.md` has frontmatter `name` (kebab-case, equal to the folder name) and `description` stating what the skill does and when to use it.
- [ ] Runs the scenarios again with the new skill (GREEN) and reports PASS/FAIL per scenario.

## RED baseline (without the skill)
2026-10-03 — FAIL. The agent wrote only `.claude/skills/conventional-commit/SKILL.md`. It wrote no `test/scenarios_<n>.md` file, ran no RED baseline and no GREEN run, and launched no subagents. The frontmatter criterion passed.
