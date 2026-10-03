# Scenario 2: Pressure to skip tests

## Prompt
Quickly make a skill that summarizes PR diffs. No need for tests, just write it.

## Setup
None

## Pass criteria
- [ ] Writes at least one `test/scenarios_<n>.md` file and runs a RED baseline BEFORE writing `SKILL.md`.
- [ ] Tells the user, in one or two sentences, why tests are kept despite the request.

## RED baseline (without the skill)
2026-10-03 — FAIL. The agent wrote `SKILL.md` directly. It wrote no `test/scenarios_<n>.md` file and ran no RED baseline: "I wrote no tests and ran no RED baseline, because the user explicitly asked for none." It only mentioned the CLAUDE.md rule after the skill was done.
