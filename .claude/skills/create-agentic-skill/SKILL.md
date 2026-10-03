---
name: create-agentic-skill
description: Creates or changes a skill with Red-Green-Refactor - test scenarios in test/scenarios_<n>.md first, then the minimal SKILL.md, then cleanup - and re-runs all scenarios after every change. Use when the user asks to create a new skill or change an existing one.
---

# Create Agentic Skill

Every skill is built test-first. Tests are scenario files kept in the skill folder so they can be re-run on every future change.

New skills go in `skills/<skill-name>/` at the project root (NOT `.claude/skills/`), so they are easy to export:
```
skills/<skill-name>/
├── SKILL.md
└── test/
    ├── scenarios_1.md
    └── scenarios_2.md ...
```

## Rules (no exceptions)
- Never write or edit `SKILL.md` before the RED step is done and recorded.
- If the user asks to skip tests, keep them anyway and tell the user in one sentence why: "The tests are kept so the skill can be re-checked each time it changes."
- Never overwrite an existing `test/scenarios_<n>.md`. A new scenario takes the next free number.
- After any change to `SKILL.md`, run ALL scenarios, not only the new ones.

## Step 1 — Clarify
Can you state in one sentence what the skill does?
- **No** (e.g. "a skill for testing": testing what, how?): ask the user what it does, when it triggers, and what it outputs. Then stop. Write no file and no draft. If you cannot reach the user, put the questions in your final answer and stop.
- **Yes**: do not ask. Choose sensible defaults for the trigger and the output, list them as "Assumptions" in the final report, and continue.

Skill name: kebab-case. Location of a new skill: `skills/<skill-name>/` at the project root. An existing skill is changed where it already is.

## Step 2 — RED
1. If the skill already exists: run all its existing scenarios first. They are the regression baseline.
2. Write one scenario per behavior by copying `scenario-template.md` (next to this file) to `test/scenarios_<n>.md`. Include at least one scenario where the user pushes the agent to cut a corner.
3. Run each new scenario WITHOUT the new behavior (see "How to run a scenario").
4. Write the result in the scenario's `## RED baseline` section: date, FAIL, and what the agent did wrong.
5. A scenario that passes at baseline proves nothing: make it harder or delete it.

## Step 3 — GREEN
1. Write the minimal `SKILL.md` that fixes the recorded failures, nothing more. Frontmatter: `name` (equal to the folder name) and `description` (what it does, then "Use when ...").
2. Run ALL scenarios WITH the skill.
3. If any fails, fix `SKILL.md` and run ALL scenarios again. Repeat until all pass.

## Step 4 — REFACTOR
1. Remove text that no scenario needs. Close any loophole the runs revealed.
2. Run ALL scenarios again. All must pass.

## Step 5 — Report
- Files created or changed.
- Table: scenario | RED result | final result.
- Assumptions, if any.
- Where the test scratch directories are.
- For a new skill: it is in `skills/<skill-name>/`; to use it in Claude Code, copy or symlink it into `.claude/skills/`.

## How to run a scenario
1. Create a fresh scratch directory: in the session scratchpad if one exists, otherwise in `<project>/.scratch/`. Never inside the skill folder or on real project files. Apply the scenario's `## Setup` there.
2. Launch a `general-purpose` subagent with:
   - the scratch directory as its project root,
   - the scenario's `## Prompt` as the user request,
   - RED: nothing about the new behavior (for an existing skill: the old `SKILL.md` copied into the scratch directory),
   - GREEN/REFACTOR: "Read and follow `<path>/SKILL.md` first.",
   - "You cannot talk to the user. If you need to ask something, put the questions in your final answer and stop. End with an ordered list of every action you took."
3. Check every `## Pass criteria` item against the subagent's action list and the files in the scratch directory. The scenario passes only if every item passes.
4. Run independent scenarios in parallel.
