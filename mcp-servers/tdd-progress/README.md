# tdd-progress

Deterministic progress tracking for the `tdd-loop` workflow. It decides, with no judgment, which task can start and whether a feature is finished.

| File | Role |
|---|---|
| `progress.py` | The rules and a command line. Standard library only. |
| `server.py` | MCP server (stdio) that exposes the same operations. Needs the packages of `requirements.txt`: the install script puts them in `.venv`. |
| `test_progress.py`, `test_server.py` | Unit tests: `python3 -m unittest discover -s mcp-servers/tdd-progress`. |

## Data

One feature is one folder in the project that uses the workflow:

```
specs/<feature>/
├── spec.md
├── progress.json
├── tasks/
│   ├── T1.md
│   └── T2.md
└── real-testing/
    └── T1/        what the real tester used and saw for the task T1 (programs, outputs, screenshots)
```

```json
{
  "feature": "login",
  "status": "open",
  "test_command": "cmake --build build && ctest --test-dir build",
  "tasks": [
    {"id": "T1", "title": "Reject an empty password", "file": "tasks/T1.md",
     "depends_on": [], "status": "done", "rejections": 0, "note": "",
     "review": "APPROVED\n- test_rejects_empty_password",
     "real_testing": "PASSED\n- B1: ran the program with an empty password -> it printed 'password required'"},
    {"id": "T2", "title": "Lock after 3 failures", "file": "tasks/T2.md",
     "depends_on": ["T1"], "status": "new", "rejections": 0, "note": ""}
  ]
}
```

## Rules

- A task goes `new -> dev -> review -> real-testing -> done`. A review or a real test can send it back: `review -> dev`, `real-testing -> dev`. Any other move is refused.
- `new -> dev` is refused while a task of `depends_on` is not `done`.
- `review -> real-testing` needs the reviewer output as note: its first line is `APPROVED`. It is kept in the field `review` of the task.
- `real-testing -> done` needs the real tester output as note: its first line is `PASSED`. It is kept in the field `real_testing` of the task. The move then runs `test_command` from the project root. It is refused while the command fails.
- `review -> dev` and `real-testing -> dev` need a note (the remarks). It is kept in the field `note` of the task and adds 1 to `rejections`. At 3 rejections the task is escalated: the human partner decides.
- `create` refuses a duplicate id, an unknown dependency, a dependency cycle, and a feature that has already started.
- `verify` looks at every feature that is `open` and has at least one task out of `new`. It fails while a task is not `done` or the test command fails. When both checks pass, the feature becomes `closed`.

## Git

These rules apply when the project root is the top folder of a git repository and is on a branch. In any other project, the tool runs no git command and the rules above do not change.

- **One branch per feature.** `new -> dev` on the default branch creates the branch `feature/<feature>` and switches to it. The default branch is the one that `origin/HEAD` names, else `main` or `master`. On any other branch, the tool stays on it. The move is refused when the branch cannot be created.
- **One commit per task.** `real-testing -> done` commits every change of the project, except the build folders, with the message `<feature> <task id>: <title>` (example: `login T1: Reject an empty password`). The result has `commit`: the short hash. The move is refused while the commit fails (a pre-commit hook that fails, for example): the task stays `real-testing`.
- **No build folder in a commit.** Before a task starts and before each commit, the tool makes git ignore the build folders. A build folder is a folder named `build`, `cmake-build-*`, `out`, `dist`, `target`, `node_modules`, `__pycache__`, `.venv` or `venv`, at any depth, or a folder that holds a file `CMakeCache.txt`, whatever its name. The tool writes them in `.git/info/exclude`: git ignores them in this clone only, and no file of the project changes. What `.gitignore` names is not committed either. Two limits:
  - A folder that holds a tracked file is never ignored. So a build folder that is already committed stays in git: remove it with `git rm -r --cached <folder>`, then commit.
  - A new folder with one of these names is not committed. To commit it, run `git add -f <folder>` once: it then holds a tracked file.
- **One commit for the end.** When a feature becomes `closed`, the tool commits `progress.json` alone, with the message `<feature>: closed`.
- **One pull request per feature.** `pr` closes the feature as `verify` does, pushes its branch to `origin`, then opens the pull request with the GitHub command line: `gh pr create`. The title is the feature name. The body lists the tasks and the test command. It is refused when a task is not `done`, the test command fails, the branch is the default branch of `origin`, the push fails or `gh` fails. When only `gh` fails, the branch is pushed: open the pull request by hand.

## Parallel tasks

Tasks that can run at the same time are each developed in their own git worktree, then merged in the project root. The rules of `## Git` still apply: the worktrees start from the branch of the feature, and each task is one commit on it.

- `new -> dev` gives the task a worktree when another task is ready or in progress. The worktree is the folder `.worktrees/<feature>/<task id>`, on the branch `tdd/<feature>/<task id>`, created from the last commit of the project root. This commit holds the work of every task of `depends_on`: they are all `done`, so each one is already merged or committed there. The field `worktree` of the task keeps its path. A task that has no other task to run with is developed in the project root.
- A worktree needs three things: the project root is the top folder of a git repository and is on a branch, the repository has a commit, and no change is uncommitted outside `specs/`. When one is missing, the task is developed in the project root, and the result of the move has `no_worktree`: the reason. Exception: while another task has a worktree, the move is refused with the reason and the task stays `new`, because it cannot share the project root with the tasks that run in their worktree.
- `real-testing -> done` for a task with a worktree does these steps in order. When a step fails, the move is refused and the task stays in `real-testing` with its worktree. A merge conflict in step 2 is the exception:
  1. It moves the folder `specs/<feature>/real-testing/<task id>/` of the worktree, if the real tester wrote it there, to the project root. Then it commits what is not committed in the worktree, except `specs/` and the build folders.
  2. It merges the last commit of the project root into the worktree. On a conflict, it cancels the merge and sends the task back to `dev` itself, as a rejection: the result of the move has the status `dev`, `note` names the files in conflict and the `git merge` command to run in the worktree, and `rejections` gets 1 more. The developer resolves the conflict in the worktree, then the task is reviewed and really tested again.
  3. It runs `test_command` in the worktree.
  4. It adds one commit `<feature> <task id>: <title>` to the branch of the project root. This commit holds the content of the worktree. Before this step, the project root does not change.
  5. It runs `test_command` in the project root, as for every task.
  6. It puts the other changes of the project root (`progress.json`, what the real tester kept) in the commit of step 4: the task is one commit. The result has `commit`: its short hash.

  Then it removes the worktree, its branch and the field `worktree`.
- `.worktrees/` is added to `.git/info/exclude`: git does not show it in the project root.
- Two `update` calls on one feature at the same time run one after the other. Not on Windows: there, call `update` one at a time.
- The tool refuses to run from inside a worktree: it runs from the project root.

Limits:

- A worktree holds only the files that git tracks. A build folder or installed dependencies are not in it: set them up in the worktree if the test command needs them.
- A test runner that also searches the hidden folders finds the tests of `.worktrees/`: exclude this folder in its configuration.

## MCP tools

| Tool | Does |
|---|---|
| `progress_create(feature, test_command, tasks)` | Creates `progress.json`, every task `new`. |
| `progress_next(feature)` | Lists the `ready` tasks (new, all dependencies done), the tasks in `dev`, `review` and `real-testing`, the `escalated` and `waiting` ones, `finished` and the `test_command`. |
| `progress_update(feature, task_id, status, note)` | Moves one task to its next status. `note` is the output of the reviewer or of the real tester: required for `real-testing`, for `done` and for a rejection. Creates and merges the worktree of a parallel task. |
| `progress_pull_request(feature)` | Closes a finished feature, pushes its branch and opens its pull request. The result has `branch` and `url`. |
| `progress_status(feature)` | Gives the summary and the dashboard (see below) of one feature. With no name: of every feature. |

Register the server in your tool with this command, started from the project root:

```
python3 mcp-servers/tdd-progress/server.py
```

Example for a tool that reads an `mcpServers` JSON config:

```json
{"mcpServers": {"tdd-progress": {"command": "python3", "args": ["mcp-servers/tdd-progress/server.py"]}}}
```

The project root is the folder the server starts in. Set `TDD_PROGRESS_ROOT` to use another one.

## Command line

Same operations, same rules, no dependency. The stop hook `hooks/tdd_gate.py` runs `verify`: register it in your tool as a hook that runs when the agent stops. The file `README.md` at the root of this repository says when this hook blocks the stop.

```
python3 mcp-servers/tdd-progress/progress.py create <feature> --test-command "<command>" --tasks tasks.json
python3 mcp-servers/tdd-progress/progress.py next <feature>
python3 mcp-servers/tdd-progress/progress.py update <feature> <task> <dev|review|real-testing|done> [--note "<agent output>"]
python3 mcp-servers/tdd-progress/progress.py status [<feature>] [--json]
python3 mcp-servers/tdd-progress/progress.py verify
python3 mcp-servers/tdd-progress/progress.py pr <feature>
```

`tasks.json` is a list: `[{"id": "T1", "title": "...", "depends_on": []}]`. Every command prints JSON and exits `0`, except `status`: it prints the dashboard, and the summary as JSON with `--json`. A refusal prints `ERROR: <reason>` on standard error and exits `1`. `verify` prints `{}` and exits `0`, or prints one `FAIL:` line per problem and exits `1`.

## Dashboard

`status` shows every feature and its tasks. Give a feature name to show only that feature.

```
$ python3 mcp-servers/tdd-progress/progress.py status
login (open): 1 of 3 tasks done
  TASK  STATUS          REJECTIONS  TITLE
  T1    done            0           Reject an empty password
  T2    dev, escalated  3           Hash the password
  T3    new             0           Lock after 3 failures

signup (closed): 1 of 1 tasks done
  TASK  STATUS  REJECTIONS  TITLE
  T1    done    0           Send the welcome mail
```

- The first line of a block is the feature, `open` or `closed`, and its number of tasks that are `done`.
- `REJECTIONS` is the number of times the task was sent back to `dev`, by the review or by the real test.
- `dev, escalated` is a task rejected 3 times: the workflow waits for the human partner.
- With no feature in `specs/`, the command prints `No feature: specs/ holds no progress.json.`

The summary is the same data for a program: `status --json` prints it, and `progress_status` returns it with the dashboard under the key `dashboard`.

```json
{"feature": "login", "status": "open",
 "counts": {"new": 1, "dev": 1, "review": 0, "real-testing": 0, "done": 1},
 "tasks": {"T1": "done", "T2": "dev", "T3": "new"},
 "rejections": {"T1": 0, "T2": 3, "T3": 0},
 "remaining": ["T2", "T3"], "finished": false}
```

## Install the workflow in a project

Run these commands from the root of your project. `A` is the path of this repository. Use `install_cursor.py` for Cursor.

```
A=/path/to/Agentic
$A/install_claude.py workflow/tdd-loop workflow/tdd-bugfix
```

`workflow/tdd-loop` is the way of a feature, `workflow/tdd-bugfix` is the short way of a bug: install one or both. The script copies their skills, the three agents, the stop hook and this server into the project, and registers the server and the hook in the config files of the tool. It also creates the Python environment `mcp-servers/tdd-progress/.venv`, installs `requirements.txt` in it, and makes the tool start the server with it. The file `README.md` at the root of this repository gives the details.

Start the tool in the project. Accept the MCP server `tdd-progress` and the hook when it asks. Then:

1. Write `/tdd-elaborate <what the feature does, and the command that runs the tests>`. Answer the questions, if any.
2. Read `specs/<feature>/spec.md` and say that you approve it. The plan and the development follow with no other pause.
3. To continue a feature in a later session, write `Continue the feature <feature>`.
4. To see where every feature is, write `Show the progress`, or run `python3 mcp-servers/tdd-progress/progress.py status` in a terminal.
5. To fix a bug, write `/tdd-bugfix <the input, the result you get, the result you expect>`. A test that fails proves the bug first. Then the fix is developed, reviewed and really tested as the one task of the feature `fix-<name>`, with no spec to approve and no plan.
6. In a git repository, nothing more to do: the feature gets its branch `feature/<feature>`, each done task is one commit, and the pull request is opened at the end (see `## Git`). The pull request needs the GitHub command line `gh`, signed in.
