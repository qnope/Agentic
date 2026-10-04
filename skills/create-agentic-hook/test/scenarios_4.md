# Scenario 4: Hook must not trap the agent in a loop

## Prompt
Create a hook that stops the agent from finishing while `pytest` is still running.

## Setup
None

## Pass criteria
- [ ] Exactly one non-test `.py` file exists directly in `hooks/` at the scratch directory root.
- [ ] After starting `python3 -c "import time; time.sleep(120)" pytest` in the background, `echo '{}' | python3 hooks/<file>.py` exits with code 2.
- [ ] With the same background process still running, `echo '{"stop_hook_active": true}' | python3 hooks/<file>.py` exits with code 0. The background process is killed afterwards.
- [ ] A test file `hooks/test_*.py` exists and its text contains `stop_hook_active`.
- [ ] `python3 -m unittest discover -s hooks` exits with code 0.

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — all 3 wrote a shell script in `.claude/hooks/`, no Python, no `hooks/test_*.py`. Runs 1, 2 and 3 did not check `stop_hook_active` (each said so in its report). Note: parallel runs matched each other's processes (`pgrep -f` false positives), so run the checks one scenario at a time or use anchored patterns.
