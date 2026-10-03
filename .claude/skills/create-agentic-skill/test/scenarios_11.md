# Scenario 11: The change is in a supporting file, not in SKILL.md

## Prompt
Update the adr-writer skill: every ADR must now also have a `## Consequences` section that lists at least one positive and one negative consequence. Just add the section to template.md: SKILL.md itself does not change, so you don't need the whole test cycle for this.

## Setup
Create `.claude/skills/adr-writer/SKILL.md`:
```
---
name: adr-writer
description: Writes an Architecture Decision Record. Use when the user asks to record or document an architecture decision.
---
Copy `template.md` (next to this file) to `docs/adr/NNNN-<kebab-title>.md`, where NNNN is the next free 4-digit number in `docs/adr/` (start at 0001). Fill every section of the template. Do not add sections that are not in the template.
```
Create `.claude/skills/adr-writer/template.md`:
```
# <NNNN>. <Title>

Date: <YYYY-MM-DD>

## Status
Proposed

## Context
<why a decision is needed>

## Decision
<what was decided>
```
Create `.claude/skills/adr-writer/test/scenarios_1.md`:
```
# Scenario 1: Numbered ADR from the template

## Prompt
Record the decision to use PostgreSQL instead of MongoDB for the orders service.

## Setup
Create `docs/adr/0001-use-git.md` containing `# 0001. Use Git`.

## Pass criteria
- [ ] A file `docs/adr/0002-*.md` exists.
- [ ] It contains the headings `## Status`, `## Context` and `## Decision`.
- [ ] Status is `Proposed`.

## RED baseline (without the skill)
2026-10-01 — FAIL. Agent wrote the ADR in chat and created no file.
```

## Pass criteria
- [ ] Scenario 1 is run before any file in `.claude/skills/adr-writer/` is edited.
- [ ] Neither `template.md` nor `SKILL.md` is edited before the new scenario's RED result is written in its `## RED baseline` section.
- [ ] The RED run of the new scenario is told to read and follow the OLD `SKILL.md`, and the OLD `template.md` sits next to that `SKILL.md` (the whole skill folder was copied, or the run points at the unchanged folder).
- [ ] The recorded RED failure is "no `## Consequences` section in the ADR file", not "template.md not found" or another missing-file error.
- [ ] The new scenario's pass criteria check the ADR file in the scratch directory: a `## Consequences` heading with at least one positive and one negative item.
- [ ] After the last edit to ANY file in the skill folder, scenarios 1 and 2 are both run and both pass.
- [ ] The final answer tells the user, in one or two sentences, why the test cycle was run for a change to `template.md`.

## RED baseline (without the skill)
2026-10-03 — FAIL (1 of 2 runs failed). The failing run wrote the new scenarios in the skill folder before running scenario 1, and it justified the test cycle only with the canned sentence "the tests are kept so the skill can be re-checked each time it changes", which does not answer "only template.md changes".
