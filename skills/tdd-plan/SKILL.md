---
name: tdd-plan
description: Splits an approved spec `specs/<feature>/spec.md` into task files, one feature per task, and creates the progress file with the tdd-progress tool. It is the second step of the tdd-loop workflow and writes no code. Use when the user asks to plan a feature or to split a spec into tasks, or after tdd-elaborate when the spec is approved.
---

# TDD Plan

Second step of the `tdd-loop` workflow: `tdd-elaborate -> tdd-plan -> tdd-implement`. This step writes the task files and creates the progress file. Nothing else.

## Rules (no exceptions, even if the human partner asks)
1. **Approved spec only.** `specs/<feature>/spec.md` must contain the line `Status: approved`. If it does not: write no file, do not change the status yourself, say that the spec is not approved and ask the human partner to approve it.
2. **The tool writes the progress file.** Never write or edit `specs/<feature>/progress.json` yourself, even if the user says to write it by hand. Create it with the tool `progress_create` of the MCP server `tdd-progress`. If you do not have this tool, run the same operation on the command line (Step 3). In the final output, name the one you used: `progress_create` or `progress.py`.
3. **Plan only.** Write no code and no test. Do not change the spec. Create no other file than the task files.
4. **Tests of behavior only.** A test gives an input to the code and checks its result. Never plan a test of the build system (a build file, a target, a dependency), of a convention (names, format, comments, documentation) or of the structure of the files (a file exists, where a function or a class is). A behavior of the spec that is about one of them has no line in `## Tests to write` and no task of its own: copy it in the `## Behaviors` of a task that has a test.

## Step 1 — Split the spec into tasks
- A task is one feature: behaviors that a user uses together, and that can be tested from end to end. Do not split a feature into one task per behavior: the developer does one Red-Green-Refactor cycle per behavior inside the task.
- All the behaviors of the spec go in one task, except in these two cases:
  - **Independent parts.** Two parts are independent when no part needs the code of the other and they change different files. Each independent part is its own task, and these tasks do not depend on each other: they are developed at the same time, each in its own worktree.
  - **Above 60 minutes.** A task is 60 minutes at most for the human partner. Estimate each task: the minutes the human partner would need to write its tests and its code by hand. Above 60 minutes, split the task into tasks that each give a feature that works from end to end. A later task depends on the earlier one.
- If one behavior alone is above 60 minutes: write no file. Name the behavior, say that a task is 60 minutes at most, and ask the human partner to split the behavior in the spec.
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

## Acceptance criteria
- A1: <one use of the whole feature from end to end, the way its user does it: the steps and the result>

## Tests to write
- <one test: the input and the expected result>

## Estimate
<number> minutes

## Depends on
<task ids separated by commas, or `None`>
```

`## Acceptance criteria` holds 1 to 3 criteria, `A1` to `A3`. Each one is a use of the whole feature from end to end: it combines behaviors of the task.

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
List the tasks: id, title, estimate, depends on. Say that the next step is `tdd-implement`. If the skill `tdd-implement` is available, continue with it.
