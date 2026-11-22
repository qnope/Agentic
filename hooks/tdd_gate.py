#!/usr/bin/env python3
"""Stop hook: block the stop while a started feature has unfinished tasks or failing tests."""
import json
import subprocess
import sys

COMMAND = ["python3", "mcp-servers/tdd-progress/progress.py", "verify"]
RESUME = ("Continue the skill tdd-implement where it stopped: call progress_next, then go on from the status of "
          "each task. If an agent that you started still works on a task, wait for its output: do not start it again.")


def failures(command):
    """Run the check once. Return the failed lines, or [] if it passes."""
    done = subprocess.run(command, capture_output=True, text=True)
    if done.returncode == 0:
        return []
    lines = (done.stdout + done.stderr).splitlines()
    return [l for l in lines if l.startswith(("FAIL", "ERROR"))] or lines[-10:]


def main(stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    try:
        data = json.load(stdin)
    except ValueError:
        data = {}
    # An agent works in the background: the main agent only waits for it, and this hook runs again later.
    tasks = data.get("background_tasks")
    waits = isinstance(tasks, list) and any(isinstance(t, dict) and t.get("type") == "subagent" for t in tasks)
    failed = [] if data.get("stop_hook_active") or waits else failures(COMMAND)
    if failed:
        print("The tdd-loop workflow is not finished:\n" + "\n".join(failed) + "\n" + RESUME, file=stderr)
        return 2
    print("{}", file=stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
