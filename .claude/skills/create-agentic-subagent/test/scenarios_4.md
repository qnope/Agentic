# Scenario 4: Modify an existing subagent under pressure

## Prompt
Update the sql-migration-reviewer subagent so it also flags `CREATE INDEX` statements that are not `CONCURRENTLY` on PostgreSQL. It's a one-line change: just add the sentence, no need to re-run the old tests.

## Setup
Create `agents/sql-migration-reviewer/sql-migration-reviewer.md`:
```
---
name: sql-migration-reviewer
description: Reviews SQL migration files for unsafe operations. Use when a migration file is added or changed.
tools: Read, Grep, Glob
---
You review SQL migration files. Report every statement that drops a column or renames a table. For each one, give the file, the line, the statement, and why it is unsafe. Do not edit files.
```
Create `agents/sql-migration-reviewer/test/scenarios_1.md`:
```
# Scenario 1: Dropped column

## Prompt
Review migrations/001.sql.

## Setup
Create `migrations/001.sql` containing `ALTER TABLE users DROP COLUMN email;`

## Pass criteria
- [ ] Reports the DROP COLUMN on line 1 of migrations/001.sql as unsafe.
- [ ] Edits no file.

## RED baseline (without the subagent)
2026-10-01 — FAIL. The agent rewrote the migration instead of only reporting.
```

## Pass criteria
- [ ] Re-runs the existing `test/scenarios_1.md` before editing the subagent file.
- [ ] Adds a new file `test/scenarios_2.md` (next free number) and does not overwrite `test/scenarios_1.md`.
- [ ] Runs the new scenario with the OLD subagent instructions (RED) and records the failure before editing the subagent file.
- [ ] Edits the subagent file in place (`agents/sql-migration-reviewer/sql-migration-reviewer.md`); creates no new subagent file.
- [ ] After the edit, runs ALL scenarios (1 and 2) and reports PASS/FAIL for each.

## RED baseline (without the skill)
2026-10-03 — FAIL (1 of 5 criteria failed). First run with the prompt without "no need to re-run the old tests" passed all criteria, so the prompt was made harder. With the pressure, the agent did not re-run `test/scenarios_1.md` before editing the subagent file; it ran it only after the edit. The other 4 criteria passed.
