---
name: tdd-plan
description: Splits an approved spec `specs/<feature>/spec.md` into small task files and creates the progress file with the tdd-progress tool. It is the second step of the tdd-loop workflow and writes no code. Use when the user asks to plan a feature or to split a spec into tasks, or after tdd-elaborate when the spec is approved.
---

# TDD Plan

Second step of the `tdd-loop` workflow: `tdd-elaborate -> tdd-plan -> tdd-implement`. This step writes the task files and creates the progress file. Nothing else.

## Rules (no exceptions, even if the human partner asks)
1. **Approved spec only.** `specs/<feature>/spec.md` must contain the line `Status: approved`. If it does not: write no file, do not change the status yourself, say that the spec is not approved and ask the human partner to approve it.
2. **The tool writes the progress file.** Never write or edit `specs/<feature>/progress.json` yourself, even if the user says to write it by hand. Create it with the tool `progress_create` of the MCP server `tdd-progress`. If you do not have this tool, run the same operation on the command line (Step 3). In the final output, name the one you used: `progress_create` or `progress.py`.
3. **Plan only.** Write no code and no test. Do not change the spec. Create no other file than the task files.

## Step 1 — Split the spec into tasks
- A task is the smallest piece that can be developed and tested alone: one behavior, or a few behaviors that cannot be tested apart.
- Every behavior of the spec (`B1`, `B2`, ...) is in exactly one task.
- Task ids are `T1`, `T2`, ... in the order of development.
- A task depends on another task only when it needs code that the other task writes. No cycle.

## Step 2 — Write the task files
One file per task, `specs/<feature>/tasks/<id>.md`, in exactly this format:

```
# <id>: <title>

## Goal
<1 to 3 sentences: what this task adds>

## Behaviors
<the lines of the spec this task covers, copied: `- B1: ...`>

## Tests to write
- <one test: the input and the expected result>

## Depends on
<task ids separated by commas, or `None`>
```

## Step 3 — Create the progress file
Call `progress_create` with:
- `feature`: the feature name.
- `test_command`: the command of the section `## Test command` of the spec, copied without the backticks.
- `tasks`: one entry per task, `{"id": "T1", "title": "<title>", "depends_on": []}`. `depends_on` holds the same ids as the section `## Depends on` of the task file.

Command line, when the tool is not available. The task list is JSON on standard input:

```
echo '[{"id": "T1", "title": "<title>", "depends_on": []}]' | python3 mcp-servers/tdd-progress/progress.py create <feature> --test-command "<command>"
```

If the tool refuses, it says why: fix the tasks and call again.

## Step 4 — Report
List the tasks: id, title, depends on. Say that the next step is `tdd-implement`. If the skill `tdd-implement` is available, continue with it.
