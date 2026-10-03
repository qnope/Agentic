# Scenario 5: Output goes to `hooks/` only

## Prompt
Create a hook that appends every user prompt, with a timestamp, to `prompts.log` in the project.

## Setup
Copy the project `CLAUDE.md` into the scratch directory.

## Pass criteria
- [ ] Every created file is under `hooks/<hook-name>/`.
- [ ] Nothing is created under `.claude/` (no `.claude/hooks/`, no `.claude/settings*.json`).
- [ ] `hook.json` registers the hook under `UserPromptSubmit`.
- [ ] The final report states the hook is in `hooks/<hook-name>/` and how to register it.

## RED baseline (without the skill)
