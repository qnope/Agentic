---
name: create-agentic-workflow
description: Creates the skills, agents, hooks and the structure file that make up a workflow (a chain of steps), by calling create-agentic-skill, create-agentic-agent and create-agentic-hook. Use when the user asks to create, write or add a workflow made of several steps.
---

# Create Agentic Workflow

A workflow is a chain of steps. Each step is a skill or an agent. A hook can gate a step. This skill does not do the work of the workflow: it creates the parts and the structure file that links them. The parts are created by the other `create-agentic-*` skills, never by hand.

## Rules (no exceptions, even if the human partner asks)
1. **Purpose unclear → ask.** If you cannot state in one sentence what the workflow does and name its steps, ask "What must the workflow do, and which steps does it have?" and write no file. Do this even if the user says not to ask. If you can, do not ask: choose sensible defaults and list them as "Assumptions" in the final output.
2. **Never write a skill, agent or hook file yourself.** Call `create-agentic-skill`, `create-agentic-agent` or `create-agentic-hook`, one call per part. This holds even if the user says to write the files directly, to skip the tests, or to go fast, and even if a called skill needs many runs: the number of runs is not a reason to skip them or to run them fewer times. If a call cannot finish (for example a run cannot start), stop, say which part is missing and why, and write nothing by hand. `create-agentic-skill` and `create-agentic-hook` always write tests. If the user asked to skip tests, say in the final output that the tests were written anyway.
3. **Create only what was asked.** No agent unless a step is an agent. No hook unless the user asked for a check or a gate. Do not create an empty `agents/` or `hooks/` folder.
4. **Not a workflow request** (one skill, one agent, one hook, a question) → do not use this skill, and create no file in `workflows/`.
5. **Tool-agnostic.** Do not create tool folders (`.claude`, `.cursor`, `.codex`) and do not edit any tool config: the user registers hooks.

## Step 1 — Plan
Write down, without creating any file: the steps in order, the kind of each (see Components_step.md), and the dependency line (see Structure_step.md).

## Step 2 — Create the parts
See Components_step.md.

## Step 3 — Write the structure file
See Structure_step.md. Write it last, so every path in it exists.

## Step 4 — Verify and report
See Verify_step.md.
