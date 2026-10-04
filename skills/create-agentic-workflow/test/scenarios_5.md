# Scenario 5: Parallel agents, no gate asked

## Prompt
Create a workflow named `draft-review`. Step 1 is an agent `drafter` that writes a short text from a topic. After it come two independent steps, each one an agent: `reviewer` lists the problems of the draft, and `fact-checker` lists the claims of the draft that must be verified. The two agents do not depend on each other.

## Setup
None

## Pass criteria
- [ ] `workflows/draft-review.md` exists and contains the exact text `drafter -> reviewer / fact-checker`.
- [ ] `agents/` contains exactly the 3 files `drafter.md`, `reviewer.md` and `fact-checker.md`. Each is at most 3072 bytes, its frontmatter has exactly the 2 keys `name` and `description`, the `description` line contains `Use when`, and the file contains the headings `## Steps` and `## Output`.
- [ ] The scratch directory contains no `hooks` folder (no gate or check was asked) and no `skills` folder.
- [ ] The scratch directory contains no `.claude`, `.cursor` or `.codex` folder.

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — all 3 wrote `workflows/draft-review.md` as prose steps ("Step 2: reviewer and fact-checker (parallel)"), never the line `drafter -> reviewer / fact-checker`. The agent files had `name`, a `description` with "Use when" and an `## Output` heading, but no `## Steps` heading (they used `## Input` and `## Task`). No `hooks/`, `skills/` or tool folder was created (those two criteria pass at baseline). Run 1's final report was only "placeholder", graded on its files. Run 2 said it found no workflow skill and wrote the files by hand. This scenario replaced a skill-based version (same reason as scenario 3).
