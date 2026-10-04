# Scenario 4: Negative check, one agent is not a workflow

## Prompt
Create one agent named `summarizer` that summarizes a file in at most 3 sentences.

## Setup
None

## Pass criteria
- [ ] The scratch directory contains no `workflows`, `skills` or `hooks` folder.
- [ ] If an `agents/` folder exists, its only entry is the file `summarizer.md`.

## RED baseline (without the skill)
2026-10-04 — PASS (0 of 3 runs failed) — expected: this is a negative check, it guards against over-triggering. All 3 ran create-agentic-agent and wrote only `agents/summarizer.md` (571 to 615 bytes); no `workflows/`, `skills/` or `hooks/` folder. This scenario replaced a skill-based version (same reason as scenario 3: nested skill cycles exceeded the subagent limit).
