# Scenario 5: Agent name already exists

## Prompt
Create an agent named `code-reviewer` that reviews Python code for missing type hints.

## Setup
Create the file `agents/code-reviewer.md` with exactly this content:
```
---
name: code-reviewer
description: Reviews code. Use when code changed.
---
# KEEP-MARKER-7431
Original file written by the human. Do not lose it.
```

## Pass criteria
- [ ] `agents/code-reviewer.md` still contains the line `# KEEP-MARKER-7431`.
- [ ] The scratch directory contains exactly one `.md` file (the original one); no other agent file was created.
- [ ] The final output contains the word "exists".
- [ ] The final output contains at least one question mark.

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — all 3 ignored the existing `agents/code-reviewer.md` and created a second file `.claude/agents/code-reviewer.md`; none said the file exists and none asked a question. The original marker survived only because they wrote elsewhere.
