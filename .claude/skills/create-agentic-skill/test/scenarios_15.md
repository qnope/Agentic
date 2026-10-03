# Scenario 15: Pass criteria must be objective

## Prompt
Create a skill that rewrites our CLI's error messages so they are clear and actionable for end users.

## Setup
None

## Pass criteria
- [ ] Every scenario's `## Setup` or `## Prompt` gives concrete input error messages (literal strings, for example `Error: ENOENT config.yml`) to rewrite.
- [ ] No pass criterion relies on a judgment word ("clear", "actionable", "friendly", "concise", "appropriate", "good", "helpful", "better") without a concrete test right next to it (for example "names the missing file", "contains one next step that starts with a verb", "at most 2 sentences", "contains no stack trace").
- [ ] Each pass criterion can be decided yes/no from the output text or files alone: two readers applying it to the same output give the same verdict.
- [ ] At least one scenario has a negative check (for example the rewritten message does not drop the file name or error code of the original).

## RED baseline (without the skill)
2026-10-03 — FAIL (2 of 2 runs). Both runs wrote criteria such as "says what went wrong in plain words" and "gives one concrete next step". Two readers could not agree on them: outputs offering two alternatives were graded as "one concrete action".
