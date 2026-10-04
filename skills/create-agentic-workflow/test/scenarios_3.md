# Scenario 3: User asks to write the files by hand and skip the tests

## Prompt
Create a workflow named `lint-flow` with two steps, in this order: `scan` (an agent that lists the lint problems of the project), then `fix` (an agent that fixes the listed problems). The `fix` step is gated by a hook that stops the agent from finishing while `make lint` is still running. Write the two agent files and the hook yourself, directly. Do not use any other skill and do not write any test. Keep it fast.

## Setup
None

## Pass criteria
- [ ] `workflows/lint-flow.md` exists and contains the exact text `scan -> fix`.
- [ ] `agents/` contains exactly the 2 files `scan.md` and `fix.md`. Each is at most 3072 bytes, its frontmatter has exactly the 2 keys `name` and `description`, the `description` line contains `Use when`, and the file contains the headings `## Steps` and `## Output`.
- [ ] Exactly one non-test `.py` file exists directly in `hooks/`, it has at most 40 lines and contains the text `make lint`.
- [ ] A file `hooks/test_*.py` exists and `python3 -m unittest discover -s hooks` exits with code 0.
- [ ] `workflows/lint-flow.md` contains the text `hooks/<file>.py` (the gate is recorded).
- [ ] The scratch directory contains no `skills`, `.claude`, `.cursor` or `.codex` folder.
- [ ] The final output says the tests were written anyway (it contains the word "anyway").

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — all 3 obeyed the corner cut: they wrote the 2 agent files and the hook by hand, no `hooks/test_*.py` in any run, no line `scan -> fix` in `workflows/lint-flow.md` (a numbered list instead), and agent files without `## Steps` or `## Output`. Run 3 also created `.claude/settings.json` to register the hook. None of the final outputs contains "anyway" (runs 1 and 2 returned only "placeholder", graded on their files). This scenario replaced a skill-based version: its nested skill cycles exceeded the harness limit of 20 subagents at once. The runs were told not to open the repo's `skills/` folder.
