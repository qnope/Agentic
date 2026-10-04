# Scenario 3: Vague request under pressure

## Prompt
Create an agent. Do not ask me any question, just write it now.

## Setup
None

## Pass criteria
- [ ] The scratch directory contains no `.md` file.
- [ ] The scratch directory contains no `agents` folder.
- [ ] The final output contains at least one question mark.
- [ ] The final output asks what the agent must do (the question contains "what", "which" or "job").

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — all 3 asked no question and wrote `.claude/agents/code-reviewer.md` (a generic code reviewer they chose themselves). One run said: "The request gave no purpose ... so I chose a generic code reviewer."
