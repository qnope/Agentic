# tdd-progress

Deterministic progress tracking for the `tdd-loop` workflow. It decides, with no judgment, which task can start and whether a feature is finished.

| File | Role |
|---|---|
| `progress.py` | The rules and a command line. Standard library only. |
| `server.py` | MCP server (stdio) that exposes the same operations. Needs `pip install -r requirements.txt`. |
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

## MCP tools

| Tool | Does |
|---|---|
| `progress_create(feature, test_command, tasks)` | Creates `progress.json`, every task `new`. |
| `progress_next(feature)` | Lists the `ready` tasks (new, all dependencies done), the tasks in `dev`, `review` and `real-testing`, the `escalated` and `waiting` ones, `finished` and the `test_command`. |
| `progress_update(feature, task_id, status, note)` | Moves one task to its next status. `note` is the output of the reviewer or of the real tester: required for `real-testing`, for `done` and for a rejection. |
| `progress_status(feature)` | Counts the tasks per status and gives the status of each task. With no name: every feature. |

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

Same operations, same rules, no dependency. The stop hook `hooks/tdd_gate.py` runs `verify`: register it in your tool as a hook that runs when the agent stops.

```
python3 mcp-servers/tdd-progress/progress.py create <feature> --test-command "<command>" --tasks tasks.json
python3 mcp-servers/tdd-progress/progress.py next <feature>
python3 mcp-servers/tdd-progress/progress.py update <feature> <task> <dev|review|real-testing|done> [--note "<agent output>"]
python3 mcp-servers/tdd-progress/progress.py status [<feature>]
python3 mcp-servers/tdd-progress/progress.py verify
```

`tasks.json` is a list: `[{"id": "T1", "title": "...", "depends_on": []}]`. Every command prints JSON and exits `0`. A refusal prints `ERROR: <reason>` on standard error and exits `1`. `verify` prints `{}` and exits `0`, or prints one `FAIL:` line per problem and exits `1`.

## Install the workflow in a project

Run these commands from the root of your project. `A` is the path of this repository. Use `install_cursor.py` for Cursor.

```
A=/path/to/Agentic
$A/install_claude.py workflow/tdd-loop
pip install -r mcp-servers/tdd-progress/requirements.txt
```

The script copies the three skills, the three agents, the stop hook and this server into the project, and registers the server and the hook in the config files of the tool. The file `README.md` at the root of this repository gives the details.

Start the tool in the project. Accept the MCP server `tdd-progress` and the hook when it asks. Then:

1. Write `/tdd-elaborate <what the feature does, and the command that runs the tests>`. Answer the questions, if any.
2. Read `specs/<feature>/spec.md` and say that you approve it. The plan and the development follow with no other pause.
3. To continue a feature in a later session, write `Continue the feature <feature>`.
