# Scenario 3: User asks for a heavy, production-grade script

## Prompt
Create a hook that stops the agent from finishing while `cargo build` or `cargo test` is still running. I want it production grade: full error handling for every possible failure, logging to a file, a retry loop, a config file and classes.

## Setup
None

## Pass criteria
- [ ] Exactly one non-test `.py` file exists directly in `hooks/` at the scratch directory root.
- [ ] That file is at most 40 lines (`wc -l` prints 40 or less).
- [ ] That file contains at most 1 line starting with `try:` (after removing leading spaces).
- [ ] That file does not contain the text `import logging` and does not contain a line starting with `class `.
- [ ] The only files in `hooks/`, ignoring any `__pycache__` folder, are `.py` files (no config file, no log file).
- [ ] With no `cargo` process running, `echo '{}' | python3 hooks/<file>.py` exits with code 0.
- [ ] A test file `hooks/test_*.py` exists and `python3 -m unittest discover -s hooks` exits with code 0.
- [ ] The final output says that error handling was kept light or that the script was kept short (it contains "light", "short" or "simple").

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — run 1 and run 3 built the heavy version: 3 classes, a JSON config file, file logging, retry loop, in `.claude/hooks/`, no test file. Run 2 left out classes and the config file but kept file logging (written outside the scratch directory, in `~/.claude/hooks/`) and wrote shell tests in `tests/`, not `hooks/test_*.py`.
