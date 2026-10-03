---
name: create-agentic-subagent
description: Creates or changes a Claude Code subagent with Red-Green-Refactor - test scenarios in agents/<agent-name>/test/scenarios_<n>.md first, then the minimal agents/<agent-name>/<agent-name>.md, then cleanup - and re-runs all scenarios after every change. Use when the user asks to create a new subagent (agent) or change an existing one.
---

# Create Agentic Subagent

Every subagent is built test-first. Tests are scenario files kept next to the subagent so they can be re-run on every future change.

New subagents go in `agents/<agent-name>/` at the project root (NOT `.claude/agents/`), so they are easy to export:
```
agents/<agent-name>/
├── <agent-name>.md
└── test/
    ├── scenarios_1.md
    └── scenarios_2.md ...
```

## Rules (no exceptions, even if the user asks)
- Never write or edit `<agent-name>.md` before the RED step is done and recorded.
- If the user asks to skip tests, keep them anyway and tell the user in one sentence why: "The tests are kept so the subagent can be re-checked each time it changes."
- Never overwrite an existing `test/scenarios_<n>.md`. A new scenario takes the next free number.
- Before any change to an existing subagent, run ALL its existing scenarios. After any change, run ALL scenarios again. Do this even if the user says the old tests do not need to run.

## Step 1 — Clarify
Can you state in one sentence the job of the subagent?
- **No** (e.g. "an agent for the backend": doing what?): ask the user what job it does, when it should be used, and what it returns. Then stop. Write no file and no draft. This holds even if the user says "don't ask, just make it": tell them in one sentence that the subagent cannot be built without these answers. If you cannot reach the user, put the questions in your final answer and stop.
- **Yes**: do not ask. Choose sensible defaults, list them as "Assumptions" in the final report, and continue.

Subagent name: kebab-case. An existing subagent is changed where it already is.

## Step 2 — RED
1. If the subagent already exists: run all its existing scenarios first, with its current file. They are the regression baseline.
2. Write one scenario per behavior by copying `scenario-template.md` (next to this file) to `test/scenarios_<n>.md`. Include at least one scenario where the user pushes the subagent to cut a corner.
3. Run each new scenario WITHOUT the new behavior (see "How to run a scenario").
4. Write the result in the scenario's `## RED baseline` section: date, FAIL, and what the test subagent did wrong.
5. A scenario that passes at baseline proves nothing: make it harder or delete it.

## Step 3 — GREEN
1. Write the minimal `<agent-name>.md` that fixes the recorded failures, nothing more. Frontmatter: `name` (equal to the folder name), `description` (what it does, then "Use when ..."), `tools` (only the tools the job needs; a read-only job gets no `Write` or `Edit`). The body is the subagent's system prompt.
2. Run ALL scenarios WITH the subagent file.
3. If any fails, fix `<agent-name>.md` and run ALL scenarios again. Repeat until all pass.

## Step 4 — REFACTOR
1. Remove text that no scenario needs. Close any loophole the runs revealed.
2. Run ALL scenarios again. All must pass.

## Step 5 — Report
- Files created or changed.
- Table: scenario | RED result | final result.
- Assumptions, if any.
- Where the test scratch directories are.
- The subagent is in `agents/<agent-name>/`; to use it in Claude Code, copy or symlink `<agent-name>.md` into `.claude/agents/`.

## How to run a scenario
1. Create a fresh scratch directory: in the session scratchpad if one exists, otherwise in `<project>/.scratch/`. Never inside the subagent folder or on real project files. Apply the scenario's `## Setup` there.
2. Launch a `general-purpose` subagent with:
   - the scratch directory as its project root,
   - the scenario's `## Prompt` as the task,
   - RED: no subagent instructions (for an existing subagent: its old `<agent-name>.md` copied into the scratch directory),
   - GREEN/REFACTOR: "Read `<path>/<agent-name>.md` and follow its body as your instructions. Use only these tools: `<the tools field>`.",
   - "You cannot talk to the user. If you need to ask something, put the questions in your final answer and stop. End with an ordered list of every action you took and every tool you used."
3. Check every `## Pass criteria` item against the test subagent's action list and the files in the scratch directory. Also check it used only the allowed tools. The scenario passes only if every item passes.
4. Run independent scenarios in parallel.
