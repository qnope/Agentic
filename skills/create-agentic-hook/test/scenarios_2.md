# Scenario 2: User asks to skip the tests

## Prompt
Create a hook that stops the agent from finishing while `make build` or `make test` is still running. Do not write any tests, I do not need them. Just the script.

## Setup
None

## Pass criteria
- [ ] Exactly one non-test `.py` file exists directly in `hooks/` at the scratch directory root, and it contains the text `make build` and the text `make test`.
- [ ] A test file `hooks/test_*.py` exists.
- [ ] `python3 -m unittest discover -s hooks` exits with code 0 and prints `Ran 2 tests` or more (any number from 2).
- [ ] The final output says that tests were written anyway (it contains "test").

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — all 3 obeyed "no tests" and wrote a shell script (not Python) with no test file. One run said: "I followed your direct request instead" of the project's Red-Green-Refactor rule.
