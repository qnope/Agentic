## Structure file

One file per workflow: `workflows/<workflow-name>.md` at the project root. The name is kebab-case. It is the only file in `workflows/` for this workflow.

Use exactly this format:

```
# Workflow: <workflow-name>

<dependency line>

## Components
- <step>: skill `skills/<step>/SKILL.md`
- <step>: agent `agents/<step>.md`
- <step>: skill `skills/<step>/SKILL.md`, gate `hooks/<hook>.py`
```

## Dependency line
- `a -> b` means b starts after a is done.
- `b / c` means b and c are independent: both start after the same previous step, in any order.
- `/` binds tighter than `->`: `b / c -> d` means d starts after both b and c.
- Example: `elaborate -> plan -> develop -> test / review`.
- Every step appears once in the line and once in Components.
- `gate` is the hook that must pass before the step is done. Add it only for a gate the user asked for.
