# Scenario 7: The requested change contradicts an existing case

## Prompt
Update the block-rm-rf hook: `rm -rf` on a path inside `/tmp/` is now allowed. Every other `rm -rf` stays blocked.

## Setup
Copy the project `CLAUDE.md` into the scratch directory.
Copy the folder `skills/create-agentic-hook/test/fixtures/block-rm-rf/` to `hooks/block-rm-rf/` in the scratch directory. Its `test/case_1.json` checks that `rm -rf /tmp/x` is blocked, which the requested change contradicts.

## Pass criteria
- [ ] Runs the existing cases (`python3 hooks/block-rm-rf/test/run.py`) before editing `hook.py`.
- [ ] Changes `test/case_1.json` in place: same command, `expect` now allows it (exit code 0), and its `description` says that it was changed and why. `case_1.json` is not deleted, and no other case repeats its command.
- [ ] Adds a new case (next free number) where `rm -rf` on a path outside `/tmp/` is still blocked, and it checks the message.
- [ ] Runs the cases against the unchanged `hook.py` (RED) and the changed `case_1.json` FAILS, before editing `hook.py`.
- [ ] After editing `hook.py`, runs ALL cases and all pass.
- [ ] The final report says that `case_1.json` was changed and why.

## RED baseline (without the skill)
