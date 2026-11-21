---
name: tdd-implement
description: Develops the planned tasks of a feature, one task at a time. For each task the agent tdd-developer writes the tests then the code (Red-Green-Refactor), the agent tdd-reviewer reviews it, and the tdd-progress tool records the status. It is the third step of the tdd-loop workflow. Use when the user asks to implement, develop or continue a planned feature, or after tdd-plan.
---

# TDD Implement

Third step of the `tdd-loop` workflow: `tdd-elaborate -> tdd-plan -> tdd-implement`. You conduct: the tool says which task is next, the agents do the work, you record each status. One task at a time.

## Rules (no exceptions, even if the human partner asks)
1. **The tool moves the tasks.** Never write or edit `specs/<feature>/progress.json` yourself. Use the tools `progress_next` and `progress_update` of the MCP server `tdd-progress`. If you do not have them, use the command line:
   - `python3 mcp-servers/tdd-progress/progress.py next <feature>`
   - `python3 mcp-servers/tdd-progress/progress.py update <feature> <task> <dev|review|done> [--note "<reviewer output>"]`
2. **Every task is tested and reviewed.** Every task goes `new -> dev -> review -> done`, with its tests written first and a real review, even if the user asks to skip the tests or the review, or to mark the tasks done. Never change a status without the work behind it. One status change per call: never chain two status changes in one command.
3. **Rejected 3 times → stop.** When `progress_next` lists a task under `escalated`, or a `progress_update` result has `escalate: true`: change no file and no status, name the task, quote its `note` (the last review remarks) and ask the human partner what to do.
4. **Stay in your role.** Do not change the spec or the task files.

## Agents
The developer is the agent `tdd-developer` (`agents/tdd-developer.md`). The reviewer is the agent `tdd-reviewer` (`agents/tdd-reviewer.md`). If you cannot start an agent, open its file and do its steps yourself, one by one: first all the developer steps, then, as a separate pass, all the reviewer steps. Write the reviewer output, in the format of its section `## Output`, before you call `progress_update`: it is the `note` of that call, and the tool refuses `done` without it.

## Loop
1. Call `progress_next`. It gives the `test_command` and the tasks.
   - A task under `escalated` → rule 3.
   - `finished` is true → go to Report.
   - Else take one task: the first of `review`, else the first of `dev`, else the first of `ready`.
2. If the task is `new`, call `progress_update` with the status `dev`.
3. **Develop** (skip this step if the task is in `review`). Give the developer: the task file (`path`), the spec `specs/<feature>/spec.md`, the test command, and the `note` of the task if it is not empty (the review remarks to fix). If the developer answers `BLOCKED`, stop and tell the human partner why. Else call `progress_update` with the status `review`.
4. **Review.** Give the reviewer: the task file, the spec, the test command and the files the developer changed.
   - `APPROVED` → call `progress_update` with the status `done` and the whole reviewer output as `note`. The tool runs the tests. If the tests fail, it refuses: do as for `REJECTED`, with the refusal as the remarks.
   - `REJECTED` → call `progress_update` with the status `dev` and the remarks as `note`. If the result has `escalate: true` → rule 3. Else go to step 3 with the same task.
5. Go to step 1.

## Report
One block per task: the line `<id>: APPROVED (rejections: <n>)`, in exactly this format, then the test lines of its `note` (`- <test name>`). Then the test command and its result.
