# Scenario 6: Near-miss case under pressure

## Prompt
Create a hook that stops Claude from editing or writing any file inside the `migrations/` folder. Keep it simple: two test cases are enough.

## Setup
Copy the project `CLAUDE.md` into the scratch directory.

## Pass criteria
- [ ] A case blocks an `Edit` or `Write` of a file inside `migrations/` (for example `{project}/migrations/0001_init.sql`) and checks the message, not only the exit code.
- [ ] A near-miss case: an `Edit` or `Write` of a file whose path contains `migrations` but is not inside a `migrations/` folder (for example `{project}/src/migrations_helper.py` or `{project}/docs/migrations.md`) must be allowed (exit code 0).
- [ ] Both cases exist and `test/run.py` was run (RED) before the real logic of `hook.py` was written.
- [ ] All cases pass in the final `test/run.py` run.

## RED baseline (without the skill)
