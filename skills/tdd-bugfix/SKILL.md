---
name: tdd-bugfix
description: Fixes a reported bug with no spec to approve and no plan. First a test that fails because of the bug, then the skill tdd-implement develops the fix, reviews it and really tests it. Use when the user reports a bug or a wrong result and asks to fix it. Not for a new feature.
---

# TDD Bugfix

Short way into the `tdd-loop` workflow for a bug: `tdd-bugfix -> tdd-implement`. A failing test proves the bug, then the bug is fixed as a feature of one task.

## Rules (no exceptions, even if the human partner asks)
1. **Unclear → ask.** You must be able to write the bug as "given <input>, the result is <observed result>, the expected result is <expected result>", and to name the test command. If you cannot, ask the human partner "With which input, which result do you get, and which result do you expect?" and change no file. Do this even if the user says not to ask: a guessed expected result gives a wrong fix.
2. **The test comes first.** In this skill, never change the production code: `tdd-implement` writes the fix, after the test has failed. Do every step, even if the user says to skip the test, the review, the real test or the files, or says that the fix is one line.
3. **Not reproduced → stop.** If the new test passes, the bug is not there: fix nothing and go to "Not reproduced".
4. **Not a bug** (a new feature, a question, a refactoring) → do not use this skill and create no bug file.

## Step 1 — Reproduce (RED)
Write one test with the existing tests: it gives the input of the bug and checks the expected result. Run the test command.
- The new test fails on its check of the expected result → the bug is reproduced. Keep the line of the output that shows the failure.
- The new test passes → rule 3.

## Step 2 — Record the bug
`<bug>` is `fix-` then a short kebab-case name (example: `fix-cart-remove`). Write these two files, in exactly these formats.

`specs/<bug>/spec.md`:

```
# Bug: <bug>

## Observed
Given <input>, the result is <observed result>.

## Behaviors
- B1: given <input>, the result is <expected result>.

## Reproduced by
`<test name>` in `<test file>`: <the line of the test output that shows the failure>

## Test command
`<test command>`
```

`specs/<bug>/tasks/T1.md`:

```
# T1: <title>

## Goal
<1 sentence: what the fix changes>

## Behaviors
- B1: given <input>, the result is <expected result>.

## Tests to write
- Already written, it fails: `<test name>` in `<test file>`. Make it pass.

## Depends on
None
```

Then create the progress file with the tool `progress_create` of the MCP server `tdd-progress`: `feature` is `<bug>`, `test_command` is the test command, `tasks` is `[{"id": "T1", "title": "<title>", "depends_on": []}]`. Never write `specs/<bug>/progress.json` yourself. If you do not have the tool, use the command line:

```
echo '[{"id": "T1", "title": "<title>", "depends_on": []}]' | python3 mcp-servers/tdd-progress/progress.py create <bug> --test-command "<test command>"
```

## Step 3 — Fix (GREEN)
Do the skill `tdd-implement` (`skills/tdd-implement/SKILL.md`) for the feature `<bug>`, with all its rules: the task `T1` is developed, reviewed and really tested.

## Report
The line `RED: <test name> failed before the fix`, then the report of `tdd-implement`.

## Not reproduced
Remove the test you wrote: every file is as it was before, and no file is created. The final output is, in this order:
1. The line `NOT REPRODUCED`.
2. The code of the test you wrote and the line of the test output that shows that it passed.
3. The question "With which exact input do you get the wrong result?".
