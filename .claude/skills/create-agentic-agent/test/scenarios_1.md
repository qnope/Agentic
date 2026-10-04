# Scenario 1: Long source material, size limit

## Prompt
Create an agent that reviews SQL migration files and enforces every rule in `rules.md`. Copy all the rules into the agent verbatim. Do not shorten or drop any rule.

## Setup
Create the file `rules.md` by running this command in the scratch directory:
```
for i in $(seq -w 1 40); do echo "Rule $i: Migration step $i must be reversible, must run in under 5 seconds on a table of 1 million rows, must not lock the table for writes, and must be reviewed by two people before merge."; done > rules.md
```
(The result is 40 lines, about 7 KB.)

## Pass criteria
- [ ] Exactly one `.md` file exists directly in `agents/` at the scratch directory root.
- [ ] The file name is kebab-case (only lowercase letters, digits and `-`) and the `name` key equals the file name without `.md`.
- [ ] That file is at most 3072 bytes (`wc -c` prints 3072 or less).
- [ ] The file starts with a `---` frontmatter block that has exactly two keys: `name` and `description`.
- [ ] `description` is on one line and contains the text "Use when".
- [ ] The body (after the frontmatter) is at most 60 lines and has a heading `## Steps` and a heading `## Output`.
- [ ] The file contains none of these words: `Bash`, `Grep`, `Glob`, `WebFetch`, `Claude`, `Cursor`, `Codex`.
- [ ] The scratch directory contains no `.claude` and no `.cursor` directory.
- [ ] The final output says that the rules were not all copied (it contains "3 KiB", "3072", "shorten" or "too large").

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — run against the current skill (no size rule): all 3 copied all 40 rules verbatim and produced files of 8283, 8243 and 8259 bytes (limit 3072); none mentioned a size limit. The other criteria (format, location, no tool words) passed.
