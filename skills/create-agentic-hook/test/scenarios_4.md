# Scenario 4: Modify an existing hook

## Prompt
Update the block-rm-rf hook so it also blocks `git push --force`.

## Setup
Copy the project `CLAUDE.md` into the scratch directory.
Copy the folder `skills/create-agentic-hook/test/fixtures/block-rm-rf/` to `hooks/block-rm-rf/` in the scratch directory. It contains `hook.py`, `hook.json`, `README.md`, `test/run.py`, `test/case_1.json` (blocks `rm -rf /tmp/x`), `test/case_2.json` (allows `ls -la`).

## Pass criteria
- [ ] Runs the existing cases (`python3 hooks/block-rm-rf/test/run.py`) before editing `hook.py`.
- [ ] Adds a new case file `test/case_3.json` (next free number) or higher, and does not change `case_1.json` or `case_2.json`.
- [ ] Runs the new case against the unchanged `hook.py` (RED) and it FAILS, before editing `hook.py`.
- [ ] After editing `hook.py`, runs ALL cases (1, 2 and the new ones) and all pass.

## RED baseline (without the skill)
