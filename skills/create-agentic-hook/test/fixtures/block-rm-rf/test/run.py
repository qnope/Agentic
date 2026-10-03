#!/usr/bin/env python3
"""Runs every test/case_<n>.json against ../hook.py and prints PASS/FAIL per case.

Case file format:
{
  "description": "what this case checks",
  "setup_files": {"src/a.py": "x=1"},          optional, created in the temp project dir
  "stdin": { ...hook input JSON... },          "{project}" in any string is replaced by the temp project dir
  "expect": {
    "exit_code": 0,
    "stdout_contains": "text",                 optional
    "stderr_contains": "text",                 optional
    "files_contain": {"prompts.log": "text"}   optional, paths relative to the temp project dir
  }
}
Each case runs in a fresh temp project dir, used as cwd and as $CLAUDE_PROJECT_DIR.
Exit code: 0 if all cases pass, 1 otherwise.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
HOOK = TEST_DIR.parent / "hook.py"


def case_number(path):
    return int(re.search(r"case_(\d+)\.json$", path.name).group(1))


def run_case(path):
    case = json.loads(path.read_text())
    expect = case["expect"]
    errors = []
    with tempfile.TemporaryDirectory() as project:
        for rel, content in case.get("setup_files", {}).items():
            target = Path(project, rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        escaped = json.dumps(project)[1:-1]
        stdin = json.dumps(case["stdin"]).replace("{project}", escaped)
        env = dict(os.environ, CLAUDE_PROJECT_DIR=project)
        result = subprocess.run(
            [sys.executable, str(HOOK)], input=stdin, capture_output=True,
            text=True, cwd=project, env=env, timeout=60,
        )
        if result.returncode != expect["exit_code"]:
            errors.append(f"exit code {result.returncode}, expected {expect['exit_code']}")
        for stream in ("stdout", "stderr"):
            wanted = expect.get(f"{stream}_contains")
            if wanted is not None and wanted not in getattr(result, stream):
                errors.append(f"{stream} does not contain {wanted!r}")
        for rel, wanted in expect.get("files_contain", {}).items():
            target = Path(project, rel)
            if not target.is_file():
                errors.append(f"file {rel} missing")
            elif wanted not in target.read_text():
                errors.append(f"file {rel} does not contain {wanted!r}")
        if errors:
            errors.append(f"stdout={result.stdout.strip()!r} stderr={result.stderr.strip()!r}")
    return case.get("description", ""), errors


def main():
    cases = sorted(TEST_DIR.glob("case_*.json"), key=case_number)
    if not cases:
        print("FAIL: no test/case_<n>.json files")
        return 1
    failed = 0
    for path in cases:
        description, errors = run_case(path)
        status = "FAIL" if errors else "PASS"
        print(f"{status} {path.name}: {description}")
        for error in errors:
            print(f"     {error}")
        failed += bool(errors)
    print(f"{len(cases) - failed}/{len(cases)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
