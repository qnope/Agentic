#!/usr/bin/env python3
"""PreToolUse hook: blocks Bash commands that contain `rm -rf`."""
import json
import sys

data = json.load(sys.stdin)
command = data.get("tool_input", {}).get("command", "")
if "rm -rf" in command:
    print("Blocked: `rm -rf` is not allowed.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
