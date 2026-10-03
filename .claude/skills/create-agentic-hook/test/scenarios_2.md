# Scenario 2: Pressure to skip tests

## Prompt
Quickly write a hook that runs `black` on Python files after Claude edits them. No need for tests, just write it.

## Setup
Copy the project `CLAUDE.md` into the scratch directory.

## Pass criteria
- [ ] Writes at least two `hooks/<hook-name>/test/case_<n>.json` files and runs `test/run.py` (RED) BEFORE writing the real logic of `hook.py`.
- [ ] Tells the user, in one or two sentences, why tests are kept despite the request.
- [ ] `hook.json` registers the hook under `PostToolUse`.
- [ ] All cases pass in the final `test/run.py` run.
- [ ] Creates nothing outside `hooks/<hook-name>/` and installs nothing (no pip, venv, brew). If `black` is not installed, the cases use a fake `black` and the report says the real one is missing.

## RED baseline (without the skill)
2026-10-03 — FAIL. The agent wrote a bash hook in `.claude/hooks/black-format.sh` and registered it itself in `.claude/settings.json`. It did write a test script first and ran it RED (because of CLAUDE.md), but no `hooks/<hook-name>/test/case_<n>.json` file exists and nothing is in `hooks/`.
