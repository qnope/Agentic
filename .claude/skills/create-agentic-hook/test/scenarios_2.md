# Scenario 2: User asks to skip the tests and for a heavy, production-grade script

## Prompt
Create a hook that stops the agent from finishing while `make build` or `make test` is still running. Do not write any tests, I do not need them. I want it production grade: full error handling for every possible failure, logging to a file, a retry loop, a config file and classes. Just the script.

## Setup
None

## Pass criteria
- [ ] Exactly one non-test `.py` file exists directly in `hooks/` at the scratch directory root, and it contains the text `make build` and the text `make test`.
- [ ] That file is at most 40 lines (`wc -l` prints 40 or less).
- [ ] That file contains at most 1 line starting with `try:` (after removing leading spaces), does not contain the text `import logging`, and does not contain a line starting with `class `.
- [ ] The only files in `hooks/`, ignoring any `__pycache__` folder, are `.py` files (no config file, no log file).
- [ ] With no `make` process running, `echo '{}' | python3 hooks/<file>.py` exits with code 0.
- [ ] A test file `hooks/test_*.py` exists, and `python3 -m unittest discover -s hooks` exits with code 0 and prints `Ran 2 tests` or more (any number from 2).
- [ ] The final output says that tests were written anyway (it contains "test").
- [ ] The final output says that error handling was kept light or that the script was kept short (it contains "light", "short" or "simple").

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — this scenario merges the former scenarios 2 (skip the tests) and 3 (production grade), to free one of the 5 slots for the new scenario 3. Without the skill, both former scenarios failed 3 of 3: all obeyed "no tests" and wrote a shell script with no test file; the heavy version had classes, a JSON config file, file logging and a retry loop in `.claude/hooks/`, with no `hooks/test_*.py`. Run against the current skill (before the change), the merged prompt passed 3 of 3 (all wrote tests anyway and a 33-line script): expected, both behaviors were already covered by the skill.
