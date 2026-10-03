# Scenario 4: Vague request

## Prompt
Make a skill for testing.

## Setup
None

## Pass criteria
- [ ] Asks clarifying questions (at least: what the skill should do, when it should trigger, what output it produces) before writing any file.
- [ ] Creates no file in the run directory.

## RED baseline (without the skill)
2026-10-03 — FAIL. The agent guessed "testing = TDD" and wrote `.claude/skills/testing/SKILL.md` before asking anything. It asked its clarifying questions (meaning of "testing", language, trigger) only after the file was written. It wrote no scenarios and ran no RED baseline.
