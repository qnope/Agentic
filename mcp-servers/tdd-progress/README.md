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
└── tasks/
    ├── T1.md
    └── T2.md
```

```json
{
  "feature": "login",
  "status": "open",
  "test_command": "cmake --build build && ctest --test-dir build",
  "tasks": [
    {"id": "T1", "title": "Reject an empty password", "file": "tasks/T1.md",
     "depends_on": [], "status": "done", "rejections": 0, "note": ""},
    {"id": "T2", "title": "Lock after 3 failures", "file": "tasks/T2.md",
     "depends_on": ["T1"], "status": "new", "rejections": 0, "note": ""}
  ]
}
```

## Rules

- A task goes `new -> dev -> review -> done`. A review can send it back: `review -> dev`. Any other move is refused.
- `new -> dev` is refused while a task of `depends_on` is not `done`.
- `review -> done` runs `test_command` from the project root. It is refused while the command fails.
- `review -> dev` needs a note (the review remarks). It adds 1 to `rejections`. At 3 rejections the task is escalated: the human partner decides.
- `create` refuses a duplicate id, an unknown dependency, a dependency cycle, and a feature that has already started.
- `verify` looks at every feature that is `open` and has at least one task out of `new`. It fails while a task is not `done` or the test command fails. When both checks pass, the feature becomes `closed`.

## MCP tools

| Tool | Does |
|---|---|
| `progress_create(feature, test_command, tasks)` | Creates `progress.json`, every task `new`. |
| `progress_next(feature)` | Lists the `ready` tasks (new, all dependencies done), the tasks in `dev` and `review`, the `escalated` and `waiting` ones, and `finished`. |
| `progress_update(feature, task_id, status, note)` | Moves one task to its next status. |
| `progress_status(feature)` | Counts the tasks per status. With no name: every feature. |

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

Same operations, same rules, no dependency. The stop hook uses `verify`.

```
python3 mcp-servers/tdd-progress/progress.py create <feature> --test-command "<command>" --tasks tasks.json
python3 mcp-servers/tdd-progress/progress.py next <feature>
python3 mcp-servers/tdd-progress/progress.py update <feature> <task> <dev|review|done> [--note "<remarks>"]
python3 mcp-servers/tdd-progress/progress.py status [<feature>]
python3 mcp-servers/tdd-progress/progress.py verify
```

`tasks.json` is a list: `[{"id": "T1", "title": "...", "depends_on": []}]`. Every command prints JSON and exits `0`. A refusal prints `ERROR: <reason>` on standard error and exits `1`. `verify` prints `{}` and exits `0`, or prints one `FAIL:` line per problem and exits `1`.
