# Scenario 1: Happy path, Stop hook for build and tests

## Prompt
Create a hook that stops the agent from finishing while the build (`npm run build`) or the tests (`pytest`) are still running.

## Setup
None

## Pass criteria
- [ ] Exactly one non-test `.py` file exists directly in `hooks/` at the scratch directory root.
- [ ] That file is at most 40 lines (`wc -l` prints 40 or less).
- [ ] That file contains the text `npm run build` and the text `pytest`.
- [ ] The scratch directory contains no `.claude`, `.cursor` or `.codex` directory.
- [ ] With no `pytest` and no `npm run build` process running, `echo '{}' | python3 hooks/<file>.py` exits with code 0.
- [ ] After starting `python3 -c "import time; time.sleep(120)" pytest` in the background (its command line contains `pytest`), `echo '{}' | python3 hooks/<file>.py` exits with code 2 and prints a non-empty message on stderr. The background process is killed afterwards.
- [ ] A test file `hooks/test_*.py` exists and `python3 -m unittest discover -s hooks` exits with code 0 and prints `Ran 2 tests` or more (any number from 2).

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — all 3 wrote a shell script (`.sh`) in `.claude/hooks/` and registered it in `.claude/settings.json`: no `hooks/*.py`, a `.claude` folder was created, no `hooks/test_*.py`. Run 1 wrote shell tests in `tests/`; runs 2 and 3 wrote no test file. None of them used the `hooks/` folder.
