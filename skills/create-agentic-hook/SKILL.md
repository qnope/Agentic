---
name: create-agentic-hook
description: Creates a short Python "stop" hook that blocks the agent from finishing while a batch of commands (build, tests, ...) is still running, plus its unit tests. Use when the user asks to create, write or add a hook that checks running commands before the agent stops.
---

# Create Agentic Hook

A hook is one short Python script plus its unit tests. It works in any LLM tool, so it uses only the standard library and a simple contract.

## Rules
1. **Not a hook request** (a plain script, a question, a skill) → do not use this skill and create no file in `hooks/`.
2. **Location.** Write only `hooks/<name>.py` and `hooks/test_<name>.py` at the project root. `<name>` is snake_case. Do not create tool folders (`.claude`, `.cursor`, `.codex`) and do not edit any tool config: the user registers the hook.
3. **Always write the unit tests**, even if the user says not to. In the final output, say the tests were written anyway.
4. **Keep it short and light**, even if the user asks for "production grade". The script has at most 40 lines. It has no class, no logging, no retry loop, no config file, and at most one `try:` (around reading the input). Do not add anything else to `hooks/`. In the final output, say the script was kept short and error handling light.
5. **Contract.** The script reads JSON from standard input.
   - Exit code `2` and a message on standard error: the stop is blocked.
   - Exit code `0`: the stop is allowed.
   - If the input has `"stop_hook_active": true`, exit `0` at once, even if a command is running. This prevents an endless block.
   - Unreadable input counts as `{}`.
6. **Tests.** Use only `unittest`. Replace `running` with a mock: a test never starts a real process. Cover at least: nothing running, a command running, `stop_hook_active` true while a command is running, invalid input.
7. **Verify before the final output.** Run `python3 -m unittest discover -s hooks` (all green) and `wc -l hooks/<name>.py` (40 or less).

## Script template

```python
#!/usr/bin/env python3
"""Stop hook: block the stop while a build or test command is still running."""
import json
import subprocess
import sys

PATTERNS = ["npm run build", "pytest"]


def running(patterns):
    """Return the first pattern found in a running command line, or None."""
    for pattern in patterns:
        if subprocess.run(["pgrep", "-f", pattern], capture_output=True).returncode == 0:
            return pattern
    return None


def main(stdin=sys.stdin, stderr=sys.stderr):
    try:
        data = json.load(stdin)
    except ValueError:
        data = {}
    if data.get("stop_hook_active"):
        return 0
    found = running(PATTERNS)
    if found:
        print(f"'{found}' is still running. Wait for it to finish.", file=stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Test template (`hooks/test_<name>.py`)

```python
import io
import unittest
from unittest.mock import patch

import <name>


def run(stdin, found):
    err = io.StringIO()
    with patch.object(<name>, "running", return_value=found):
        return <name>.main(io.StringIO(stdin), err), err.getvalue()


class HookTest(unittest.TestCase):
    def test_allows_when_nothing_runs(self):
        self.assertEqual(run("{}", None), (0, ""))

    def test_blocks_when_command_runs(self):
        code, message = run("{}", "pytest")
        self.assertEqual(code, 2)
        self.assertIn("pytest", message)

    def test_allows_when_already_blocked_once(self):
        self.assertEqual(run('{"stop_hook_active": true}', "pytest")[0], 0)

    def test_allows_on_invalid_input(self):
        self.assertEqual(run("not json", None)[0], 0)
```
