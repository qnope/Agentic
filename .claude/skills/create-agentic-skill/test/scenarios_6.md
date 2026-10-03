# Scenario 6: Keep a check that the new behavior does not happen where it should not

## Prompt
Update the sql-query skill so that every SELECT that can return many rows ends with `LIMIT 100`.

## Setup
Create `.claude/skills/sql-query/SKILL.md`:
```
---
name: sql-query
description: Writes SQL queries in the project's style. Use when the user asks for a SQL query.
---
Write SQL keywords in lowercase. Start each clause (select, from, join, where, group by, order by) on a new line.
```
Create `.claude/skills/sql-query/test/scenarios_1.md`:
```
# Scenario 1: Query style

## Prompt
Give me a SQL query that lists the email of every user created in 2025, newest first. Table: users(id, email, created_at).

## Setup
None

## Pass criteria
- [ ] All SQL keywords are lowercase.
- [ ] select, from, where and order by each start a new line.

## RED baseline (without the skill)
2026-10-01 — FAIL. Agent wrote all keywords in uppercase.
```

## Pass criteria
- [ ] Before editing `SKILL.md`, the agent writes a scenario whose pass criteria check that `LIMIT 100` is NOT added where it does not apply (for example a `count(*)` query, an `update` or a `delete`).
- [ ] That check is still in the test folder at the end. If its scenario passed at baseline, the scenario's `## RED baseline` says so and says it is kept as a regression check.
- [ ] After editing `SKILL.md`, the agent runs ALL scenarios, including that one, and reports PASS/FAIL for each.

## RED baseline (without the skill)
2026-10-03 — PASS (2 of 2 runs) with the skill as it was. Kept as a regression check: it guards that negative checks are kept and run.
