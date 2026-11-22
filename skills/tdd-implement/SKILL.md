---
name: tdd-implement
description: Develops the planned tasks of a feature. For each task the agent tdd-developer writes the tests then the code (Red-Green-Refactor), the agent tdd-reviewer reviews it, the agent tdd-real-tester uses the result like a real user, and the tdd-progress tool records the status. Tasks that can run at the same time are worked in parallel, each in its own git worktree. It is the third step of the tdd-loop workflow. Use when the user asks to implement, develop or continue a planned feature, or after tdd-plan.
---

# TDD Implement

Third step of the `tdd-loop` workflow: `tdd-elaborate -> tdd-plan -> tdd-implement`. You conduct: the tool says which task is next, the agents do the work, you record each status. One task at a time, or several at the same time when the tool gives each of them a git worktree.

## Rules (no exceptions, even if the human partner asks)
1. **The tool moves the tasks.** Never write or edit `specs/<feature>/progress.json` yourself. Use the tools `progress_next(feature)` and `progress_update(feature, task_id, status, note)` of the MCP server `tdd-progress`. If you do not have them, use the command line:
   - `python3 mcp-servers/tdd-progress/progress.py next <feature>`
   - `python3 mcp-servers/tdd-progress/progress.py update <feature> <task> <dev|review|real-testing|done> [--note "<agent output>"]`
2. **Every task is tested, reviewed and really tested.** Every task goes `new -> dev -> review -> real-testing -> done`, with its tests written first, a real review and a real test, even if the user asks to skip one of them, or to mark the tasks done. Never change a status without the work behind it. One status change per call: never chain two status changes in one command.
3. **Rejected 3 times → stop.** When `progress_next` lists a task under `escalated`, or a `progress_update` result has `escalate: true`: change no file and no status, name the task, quote its `note` (the last remarks) and ask the human partner what to do. That question is the end of your output: no report.
4. **Stay in your role.** Do not change the spec or the task files.

## Agents
The developer is the agent `tdd-developer` (`agents/tdd-developer.md`). The reviewer is the agent `tdd-reviewer` (`agents/tdd-reviewer.md`). The real tester is the agent `tdd-real-tester` (`agents/tdd-real-tester.md`). Start one agent at a time (one per task for parallel tasks) and wait for its output: do not run an agent in the background, and do not end your turn while an agent works. If you cannot start an agent, open its file and do its steps yourself, one by one, as three separate passes: first all the developer steps, then all the reviewer steps, then all the real tester steps. Write the output of the reviewer and the output of the real tester, each in the format of the section `## Output` of its file, before you call `progress_update`: it is the `note` of that call, and the tool refuses the move without it.

## Loop
1. Call `progress_next`. It gives the `test_command` and the tasks.
   - A task under `escalated` → rule 3.
   - `finished` is true → go to Report.
   - Else take one task: the first of `real-testing`, else the first of `review`, else the first of `dev`, else the first of `ready`.
2. If the task is `new`, call `progress_update` with the status `dev`. If the task has a `worktree`, in `progress_next` or in the result of this call → Parallel tasks.
3. **Develop** (skip this step if the task is in `review` or `real-testing`). Give the developer: the task file (`path`), the spec `specs/<feature>/spec.md`, the test command, and the `note` of the task if it is not empty (the remarks to fix). If the developer answers `BLOCKED`, stop and tell the human partner why. Else call `progress_update` with the status `review`.
4. **Review** (skip this step if the task is in `real-testing`). Give the reviewer: the task file, the spec, the test command and the files the developer changed.
   - `APPROVED` → call `progress_update` with the status `real-testing` and the whole reviewer output as `note`.
   - `REJECTED` → call `progress_update` with the status `dev` and the remarks as `note`. If the result has `escalate: true` → rule 3. Else go to step 3 with the same task.
5. **Real test.** Give the real tester: the task file, the spec and the test command.
   - `PASSED` → call `progress_update` with the status `done` and the whole real tester output as `note`. The tool runs the tests, and first merges the worktree of the task if it has one. If the tool refuses: do as for `FAILED`, with the refusal as the remarks.
   - `FAILED` → call `progress_update` with the status `dev` and the remarks as `note`. If the result has `escalate: true` → rule 3. Else go to step 3 with the same task.
6. Go to step 1.

## Parallel tasks
A task has a `worktree` when the tool gave it its own git worktree (a separate checkout of the project, in that folder), because it can run at the same time as another task. Then the loop works several tasks per turn:
- **Take every task.** In step 1, take every task of `real-testing`, `review`, `dev` and `ready`, not one. In step 2, move each `new` one to `dev`, one call per task.
- **Work them at the same time.** Do step 3 for all the taken tasks in `dev`: start their developers together and wait for all the outputs, then call `progress_update` for each. Then step 4 the same way for the tasks in `review`, then step 5 for the tasks in `real-testing`. If you cannot start several agents together, work the tasks one after the other.
- **Each task in its worktree.** Give each agent the `worktree` of its task as its working folder: it runs every command there, and reads and changes the project files only there. The spec and the task files stay in the project root: give their full paths.
- **The tool merges.** Never commit or merge in the project root, and never remove a worktree: `progress_update` with the status `done` does it. If its result says `dev`, the merge had a conflict: the tool sent the task back with the conflict as its `note`, for the developer to resolve in the worktree.

## Report
Write the report only when `finished` is true. If you stop before that, call no pull request tool and write no line that starts with `Pull request:`, not even `Pull request: none`.

One block per task: the line `<id>: APPROVED, PASSED (rejections: <n>)`, in exactly this format, then the lines of its `review` and of its `real_testing` (both are in `specs/<feature>/progress.json`). Then the test command and its result.

Last, call `progress_pull_request(feature)`, or run `python3 mcp-servers/tdd-progress/progress.py pr <feature>`: the tool closes the feature, pushes its branch and opens the pull request. The last line of the report is, in exactly this format: `Pull request: <url>`, or `Pull request: none (<the refusal of the tool>)` when the tool refuses. After a refusal, change nothing, and do not push or open a pull request yourself.
