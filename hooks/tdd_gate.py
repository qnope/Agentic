#!/usr/bin/env python3
"""Stop hook: block the stop while a started feature has unfinished tasks or failing tests."""
import json
import subprocess
import sys

COMMAND = ["python3", "mcp-servers/tdd-progress/progress.py", "verify"]


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
    failed = [] if data.get("stop_hook_active") else failures(COMMAND)
    if failed:
        print("The tdd-loop workflow is not finished:\n" + "\n".join(failed), file=stderr)
        return 2
    print("{}", file=stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
