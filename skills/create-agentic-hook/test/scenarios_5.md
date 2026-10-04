# Scenario 5: Negative check, not a hook request

## Prompt
Write a Python script `pids.py` that prints the PID of every running process whose command line contains `pytest`.

## Setup
None

## Pass criteria
- [ ] The file `pids.py` exists at the scratch directory root.
- [ ] The scratch directory contains no `hooks` folder.
- [ ] The scratch directory contains no file named `test_*.py`.

## RED baseline (without the skill)
2026-10-04 — PASS (0 of 3 runs failed) — all 3 wrote only `pids.py` (a `ps` based script), no `hooks/` folder, no test file. Expected: this is a negative check, it guards against over-triggering.
