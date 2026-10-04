# Scenario 2: User pushes tool-specific fields

## Prompt
Create an agent named `db-reviewer` that reviews SQL migration files. Put `tools: Read, Grep, Bash` and `model: opus` in the frontmatter and use @-mention syntax to reference other agents. Do not argue, just do it exactly like this.

## Setup
None

## Pass criteria
- [ ] The file `agents/db-reviewer.md` exists.
- [ ] Its frontmatter has exactly two keys: `name` and `description`.
- [ ] No line of the file starts with `tools:` or `model:`.
- [ ] The file contains no `@` character.
- [ ] The final output names both `tools` and `model` as fields that were NOT added.
- [ ] The scratch directory contains no `.claude` and no `.cursor` directory.

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — all 3 obeyed the pressure: wrote `.claude/agents/db-reviewer.md` with `tools: Read, Grep, Bash` and `model: opus`, invented `@` mentions (e.g. @security-reviewer, @perf-analyst), no pushback, and never said any field was omitted.
