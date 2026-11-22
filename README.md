# Agentic

Skills, agents, hooks, MCP servers and workflows to work with LLM coding tools.

| Folder | Content |
|---|---|
| `skills/<name>/` | A skill: `SKILL.md`, its reference files and its scenario tests in `test/`. |
| `agents/<name>.md` | An agent (subagent). |
| `hooks/<name>.py` | A stop hook and its unit tests `test_<name>.py`. |
| `mcp-servers/<name>/` | An MCP server and its unit tests. |
| `workflows/<name>.md` | A workflow: the skills, agents and hooks that work together. |

## Install a part in a project

Two scripts copy parts of this repository into a project and write the config files of the tool:

- `install_claude.py` for Claude Code,
- `install_cursor.py` for Cursor.

Run the script from the root of your project, or give the project with `--project`:

```
cd ~/my-project
/path/to/Agentic/install_claude.py workflow/tdd-loop
```

```
./install_claude.py skill/tdd-plan agent/tdd-reviewer --project ~/my-project
./install_cursor.py hook/tdd_gate --project ~/my-project
./install_claude.py
```

The last command, with no part, lists the parts of this repository and installs nothing.

A part is `<kind>/<name>`. This is where each kind goes in the project:

| Part | Claude Code | Cursor |
|---|---|---|
| `skill/<name>` | `.claude/skills/<name>/` | `.cursor/skills/<name>/` |
| `agent/<name>` | `.claude/agents/<name>.md` | `.cursor/agents/<name>.md` |
| `hook/<name>` | `hooks/<name>.py`, registered as a `Stop` hook in `.claude/settings.json` | `hooks/<name>.py` and the adapter `.cursor/hooks/<name>.py`, registered as a `stop` hook in `.cursor/hooks.json` |
| `mcp-server/<name>` | `mcp-servers/<name>/` and its Python environment `mcp-servers/<name>/.venv`, registered in `.mcp.json` | `mcp-servers/<name>/` and its Python environment `mcp-servers/<name>/.venv`, registered in `.cursor/mcp.json` |
| `workflow/<name>` | every component that `workflows/<name>.md` names | the same |

Rules:

- A part brings the parts that its text names by path. Example: `skill/tdd-implement` brings the three agents it starts and the MCP server `tdd-progress`.
- A skill is copied with its reference files: every file of its folder that is not a test.
- The tests of a part are not copied (`test/`, `test_*.py`).
- In the copied skills and agents, the path of an installed skill or agent is rewritten to its place in the project: `agents/tdd-developer.md` becomes `.claude/agents/tdd-developer.md`.
- In a config file that already exists, the script adds or updates the entry of the part and keeps every other setting. A hook is registered once.
- You can run the script again, for example after an update of this repository. Each line of its output says `created`, `updated` or `unchanged` for one file or one Python environment.
- If a part is unknown or a config file is not valid JSON, the script writes nothing and exits with code 1.

Git:

- Git ignores what the script installed. The script writes the installed paths in a block of the `.gitignore` of the project. It creates this file if the project has none. Example:

  ```
  # >>> Agentic: paths written by install_claude.py and install_cursor.py >>>
  /.claude/agents/tdd-reviewer.md
  /.claude/skills/tdd-plan/
  /.mcp.json
  /hooks/tdd_gate.py
  /mcp-servers/tdd-progress/
  # <<< Agentic <<<
  ```

- The block names only installed paths: the folder of one skill, the file of one agent, the file of one hook, the folder of one server. It never names a whole folder such as `.claude/` or `hooks/`: git still sees your own skills, agents, hooks and servers.
- Each install adds its paths to the same block, each path once. The script changes no line outside the block, and removes no line of the block.
- A config file (`.claude/settings.json`, `.mcp.json`, `.cursor/hooks.json`, `.cursor/mcp.json`) is in the block only when it holds nothing but what this install writes. A config file that also holds your own settings is not in the block: git must keep your settings. The script then prints `not ignored <file>`.
- Commit the `.gitignore` after an install that created or updated it. The workflow `tdd-loop` gives a task its own worktree only when no file outside `specs/` has an uncommitted change.
- To make git see one path of the block again, write `!<path>` on a line under the block. Example: `!/.mcp.json`.
- Git keeps a file that is already committed, even when the block names it. To remove it from git and keep it on the disk: `git rm -r --cached <path>`, then commit.
- When the project is this repository, the block names only the copies in `.claude/` or `.cursor/`. The parts themselves, such as `hooks/<name>.py` and `mcp-servers/<name>/`, stay visible to git.

Python environment of an MCP server:

- When the server has a `requirements.txt`, the script creates the virtual environment `mcp-servers/<name>/.venv` with `python -m venv`, then runs `pip install -r requirements.txt` in it. It uses the Python that runs the script.
- The config file starts the server with the Python of this environment. Nothing is installed in your own Python. A server without `requirements.txt` gets no environment and starts with `python3`.
- When you run the script again, an environment whose requirements did not change is left as it is (`unchanged`). If `requirements.txt` changed, the script runs `pip install` again in the same environment (`updated`).
- If the environment cannot be created or `pip` fails (no network, for example), the script prints the command that failed and its output, and exits with code 1. The rest is installed. Run the script again when the cause is fixed.
- The environment holds a `.gitignore`, so git does not see it. It is not copied from one machine to another: run the script on each machine.

Limits:

- Every hook is registered as a stop hook: it runs when the agent wants to stop.
- Cursor does not block a stop with an exit code. The adapter runs the hook and, if the hook blocks, gives its message to Cursor as a follow-up message, so the agent continues. It does this once: after one follow-up the agent is free to stop.
- For Cursor, the MCP server gets the environment variable `<NAME>_ROOT` (example: `TDD_PROGRESS_ROOT`) set to the workspace folder. A server of this repository reads its project root from this variable.
- The Cursor files follow the Cursor documentation. They were not tried in Cursor itself.

The tests of the scripts: `python3 -m unittest test_install`.

## The stop hook `tdd_gate`

`hooks/tdd_gate.py` is the gate of the workflows `tdd-loop` and `tdd-bugfix`. It runs when the main agent wants to stop.

| Situation | What the hook does |
|---|---|
| A started feature has a task that is not `done`, or its test command fails | It blocks the stop. Its message lists the problems, then tells the agent to continue the skill `tdd-implement` where it stopped: call `progress_next`, then go on from the status of each task. A task in `real-testing` goes on with the real test: it is not developed again. |
| An agent works in the background (the developer, the reviewer or the real tester) | It allows the stop and prints nothing: the main agent only waits. The end of the agent wakes the main agent, and the hook runs again when the main agent wants to stop. |
| The hook blocked the stop just before (`stop_hook_active`) | It allows the stop. This prevents an endless block. |
| Every started feature is finished and its tests pass | It allows the stop. |

Limits:

- The hook knows that an agent works in the background from the list `background_tasks` that Claude Code gives to a `Stop` hook: an entry with the type `subagent`. It was tried with Claude Code 2.1.330. A background shell command does not count: the hook still blocks.
- A tool that does not give this list (Cursor, an older Claude Code) makes the hook block once while an agent works in the background. The message then tells the main agent to wait for the output of this agent, and not to start it again.

The tests of the hook: `python3 -m unittest discover -s hooks`.
