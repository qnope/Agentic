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

## RED baseline (without the skill)
