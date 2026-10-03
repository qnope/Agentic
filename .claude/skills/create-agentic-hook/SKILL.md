---
name: create-agentic-hook
description: Creates or changes a Claude Code hook with Red-Green-Refactor - JSON test cases first, then a minimal Python hook, then cleanup - and writes everything to hooks/<hook-name>/ at the project root. Use when the user asks to create a new hook or change an existing one.
---

# Create Agentic Hook

Every hook is built test-first. The tests are JSON case files kept next to the hook so they can be re-run on every future change.

All output goes to `hooks/<hook-name>/` at the project root:
```
hooks/<hook-name>/
├── hook.py        # the hook, Python 3
├── hook.json      # snippet to merge into .claude/settings.json
├── README.md      # what it does, event, matcher, how to install, how to test
└── test/
    ├── run.py     # copy of run-template.py (next to this file)
    ├── case_1.json
    └── case_2.json ...
```

Hook facts (events, stdin fields, exit codes, JSON output, `hook.json` format): read `hook-reference.md` next to this file before writing any case.

## Rules (no exceptions)
- Write files only under `hooks/<hook-name>/`. Never create or edit `.claude/settings.json`, `.claude/settings.local.json` or `.claude/hooks/`. The user registers the hook.
- Install nothing (no pip, venv, brew, npm). If the hook calls an external tool, the cases use a fake one: `setup_files` → `bin/<tool>` (see `run-template.py`). If the real tool is missing, say so in the report.
- Never write the real logic of `hook.py` before the RED step is done.
- If the user asks to skip tests (also for "small" changes), keep them anyway and tell the user in one sentence why: "The tests are kept so the hook can be re-checked each time it changes."
- Never overwrite or change an existing `test/case_<n>.json`. A new case takes the next free number.
- After any change to `hook.py`, run ALL cases: `python3 hooks/<hook-name>/test/run.py`.

## Step 1 — Clarify
Can you state the hook in one sentence: which event, which condition, which effect (block, warn, log, change)?
- **No** (e.g. "a hook for security": against what, when, block or warn?): ask the user which event triggers it, what condition it checks, and what effect it has. Then stop. Write no file. If you cannot reach the user, put the questions in your final answer and stop.
- **Yes**: do not ask. Choose sensible defaults, list them as "Assumptions" in the final report, and continue.

Hook name: kebab-case.

## Step 2 — RED
1. Existing hook: run `python3 hooks/<hook-name>/test/run.py` first. It is the regression baseline.
2. New hook: copy `run-template.py` to `hooks/<hook-name>/test/run.py` and create `hook.py` as a stub that only reads stdin and exits 0.
3. Write one `test/case_<n>.json` per behavior, from `case-template.json` (format in the header of `run-template.py`). Include at least one case where the hook must act and one where it must not. A "must act" case checks the message (`stderr_contains`, `stdout_contains` or `files_contain`), not only the exit code.
4. Run `test/run.py`. Every new "must act" case must FAIL. A case that passes now proves nothing: fix it.

## Step 3 — GREEN
1. Write the minimal `hook.py` that makes the cases pass.
2. Write `hook.json` (exec form: `"command": "python3", "args": ["${CLAUDE_PROJECT_DIR}/hooks/<hook-name>/hook.py"]`) and `README.md`.
3. Run ALL cases. Fix `hook.py` until all pass.

## Step 4 — REFACTOR
Clean up `hook.py`, then run ALL cases again. All must pass.

## Step 5 — Report
- Files created or changed.
- Table: case | RED result | final result.
- Assumptions, if any.
- The hook is in `hooks/<hook-name>/`. To enable it, merge `hook.json` into `.claude/settings.json` (or `.claude/settings.local.json` for personal use).
