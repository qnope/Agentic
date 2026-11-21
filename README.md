# Agentic

Skills, agents, hooks, MCP servers and workflows to work with LLM coding tools.

| Folder | Content |
|---|---|
| `skills/<name>/` | A skill: `SKILL.md` and its scenario tests in `test/`. |
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
- The tests of a part are not copied (`test/`, `test_*.py`).
- In the copied skills and agents, the path of an installed skill or agent is rewritten to its place in the project: `agents/tdd-developer.md` becomes `.claude/agents/tdd-developer.md`.
- In a config file that already exists, the script adds or updates the entry of the part and keeps every other setting. A hook is registered once.
- You can run the script again, for example after an update of this repository. Each line of its output says `created`, `updated` or `unchanged` for one file or one Python environment.
- If a part is unknown or a config file is not valid JSON, the script writes nothing and exits with code 1.

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
