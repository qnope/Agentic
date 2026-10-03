# Scenario 1: Basic creation

## Prompt
Create a hook that blocks Bash commands containing `rm -rf`.

## Setup
Copy the project `CLAUDE.md` into the scratch directory.

## Pass criteria
- [ ] Writes at least two `hooks/<hook-name>/test/case_<n>.json` files (one where the hook must act, one where it must not) BEFORE writing the real logic of `hook.py`.
- [ ] Runs `python3 hooks/<hook-name>/test/run.py` before the real logic exists (RED) and the "must act" case FAILS.
- [ ] Output folder is `hooks/<hook-name>/` (kebab-case) and contains `hook.py`, `hook.json`, `README.md`, `test/run.py`, `test/case_<n>.json`.
- [ ] `hook.py` is Python 3. `hook.json` registers it under `PreToolUse` with matcher `Bash` and a command that points to `hooks/<hook-name>/hook.py`.
- [ ] Runs `python3 hooks/<hook-name>/test/run.py` after writing the hook (GREEN) and every case passes.
- [ ] No `.claude/settings.json` or `.claude/settings.local.json` is created or changed.
- [ ] The final report tells the user how to register the hook (merge `hook.json` into `.claude/settings.json`).

## RED baseline (without the skill)
