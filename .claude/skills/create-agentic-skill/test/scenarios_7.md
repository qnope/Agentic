# Scenario 7: The requested change contradicts an existing scenario

## Prompt
Change the sql-query skill: SQL keywords must now be written in UPPERCASE.

## Setup
Same files as in `scenarios_6.md` (copy its Setup block exactly): `.claude/skills/sql-query/SKILL.md` (lowercase keywords) and `.claude/skills/sql-query/test/scenarios_1.md` (checks lowercase keywords).

## Pass criteria
- [ ] Runs the existing `test/scenarios_1.md` before editing `SKILL.md`.
- [ ] Changes the pass criteria of `test/scenarios_1.md` from lowercase to UPPERCASE in the same file (the file is not deleted and no second scenario repeats it), and adds a dated line under its `## RED baseline` that says why the criteria changed.
- [ ] Runs the changed scenario with the old `SKILL.md` and records FAIL before editing `SKILL.md`.
- [ ] After editing `SKILL.md`, runs ALL scenarios, and all pass.
- [ ] The final report says that `test/scenarios_1.md` was changed and why.

## RED baseline (without the skill)
2026-10-03 — FAIL (4 of 5 criteria failed). Passed: it ran scenario 1 before editing `SKILL.md`. Failed: it left `test/scenarios_1.md` unchanged because "the rules forbid" overwriting it, so scenario 1 failed after the change: "no version of SKILL.md passes both 'lowercase' (scenario 1) and 'UPPERCASE' (scenarios 2 and 3)". It recorded no RED run for the changed check, skipped REFACTOR, and stopped to ask the user for permission to edit scenario 1.
