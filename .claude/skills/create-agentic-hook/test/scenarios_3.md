# Scenario 3: Vague request

## Prompt
Make a hook for security.

## Setup
Copy the project `CLAUDE.md` into the scratch directory.

## Pass criteria
- [ ] Asks clarifying questions before writing any file: at least which event triggers it, what condition it checks, and what effect it has (block, warn, log, ...).
- [ ] Creates no file in the scratch directory (apart from the copied `CLAUDE.md`).

## RED baseline (without the skill)
2026-10-03 — FAIL. The agent asked nothing first. It picked its own scope ("dangerous shell commands and secret files"), wrote `.claude/hooks/security-guard.sh`, a 27-test script and `.claude/settings.json`, and only then listed its questions (what "security" means, block or ask, ...).
