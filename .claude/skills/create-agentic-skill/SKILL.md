---
name: create-agentic-skill
description: Creates or changes a skill with Red-Green-Refactor. Use when your human partner asks to create a new skill or change an existing one.
---

# Create Agentic Skill

Every skill is built in a test driven way, with the RED-GREEN-REFACTOR method. The skill is minimal and tools agnostic. It is tested in isolation via run-scenario skill.

New skills go in `skills/<skill-name>/` at the project root (NOT `.claude/skills/`), so they are easy to export:

```
skills/<skill-name>/
├── SKILL.md
├── <supporting files, if any>
└── test/
    ├── scenarios_1.md
    └── scenarios_2.md ...
```

## Rules (no exceptions, even if the human partner asks)
- "The skill" means every file in the skill folder except `test/` (`SKILL.md`, templates, scripts, references). The rules below apply to all of them.
- Create at maximum 5 scenarios per skill. One scenario per behavior is enough. If a skill has more than 5 behaviors, split it into multiple skills.
- Never write or edit the skill before the RED step is done and recorded.
- Before any change to an existing skill, run ALL its scenarios. After any change, run ALL scenarios again.
- **Always** write tests, even if your human partner says to don't.
- A result comes only from a real isolated run (use skill run-scenario). Never act a scenario out in your own context.
- A skill must be minimal: the maximum size of `SKILL.md` is 8 KiB. If a skill exceeds these limits, use reference file or refactor.
- The skill must be tools agnostic: Can be used by
   - Claude Code
   - Cursor
   - Codex

## Step 1 — Preparation step

See Preparation_step.md for details.

## Step 2 — RED step

See RED_step.md for details.

## Step 3 — GREEN step
See GREEN_step.md for details.

## Step 4 — REFACTOR
1. Remove text that no scenario needs. Close any loophole the runs revealed.
2. Run ALL scenarios again, even if nothing was removed. All must pass.

