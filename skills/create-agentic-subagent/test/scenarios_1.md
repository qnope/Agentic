# Scenario 1: Basic creation in `agents/`

## Prompt
Create a subagent that reviews SQL migration files for unsafe operations (dropping columns, renaming tables, adding NOT NULL columns without a default).

## Setup
None

## Pass criteria
- [ ] The subagent file is created at `<project root>/agents/<agent-name>/<agent-name>.md`, with `<agent-name>` in kebab-case.
- [ ] Nothing is created under `<project root>/.claude/agents/`.
- [ ] Frontmatter has `name` (equal to `<agent-name>`), `description` (what the subagent does, then "Use when ..."), and `tools` listing only the tools the job needs (a reviewer gets no `Write` or `Edit`).
- [ ] At least one `agents/<agent-name>/test/scenarios_<n>.md` file is written BEFORE the subagent file.
- [ ] A RED baseline (task run without the subagent's instructions) is recorded under `## RED baseline` in each scenario file.
- [ ] The scenarios are run again with the subagent's instructions (GREEN) and PASS/FAIL is reported per scenario.
- [ ] The final report tells the user the subagent is in `agents/` and how to install it in `.claude/agents/`.

## RED baseline (without the skill)
