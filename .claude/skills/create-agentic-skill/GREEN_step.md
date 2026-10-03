## Green step

1. Write the minimal skill that fixes the recorded failures, nothing more. Frontmatter: `name` (equal to the folder name) and `description` (what it does, then "Use when ..."). The description decides when the skill triggers.
2. Run ALL scenarios WITH the skill.
3. If any fails, fix the skill and run ALL scenarios again. Repeat until all pass. If a trigger scenario fails, fix `description`.