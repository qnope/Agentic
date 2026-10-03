# Claude Code hook reference

Source: https://code.claude.com/docs/en/hooks.md (checked 2026-10-03). If something here looks wrong, check the source.

## Input (JSON on stdin)
Common fields: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `permission_mode` (not on every event).

| Event | Fires | Matcher filters | Extra fields |
|---|---|---|---|
| `PreToolUse` | before a tool runs | tool name | `tool_name`, `tool_input`, `tool_use_id` |
| `PostToolUse` | after a tool succeeded | tool name | `tool_name`, `tool_input`, `tool_response`, `tool_use_id` |
| `UserPromptSubmit` | user sends a prompt | no matcher | `prompt` |
| `Stop` | Claude finishes its answer | no matcher | `stop_hook_active`, `last_assistant_message` |
| `SessionStart` | session starts | `startup`, `resume`, `clear`, `compact` | `source` |
| `Notification` | Claude sends a notification | notification type | `notification_type`, `message` |

Tool input examples: `Bash` → `tool_input.command`. `Edit` / `Write` → `tool_input.file_path` (absolute path).
Other events exist (`SubagentStop`, `PreCompact`, `SessionEnd`, ...): read the source before using one.

## Exit codes
- `0`: success. stdout is parsed as JSON if it starts with `{` and ends with `}`. For `UserPromptSubmit` and `SessionStart`, plain-text stdout is added to Claude's context. stderr goes to the debug log only.
- `2`: blocking error. stderr is the message.
  - `PreToolUse`: the tool call is blocked; Claude sees stderr.
  - `UserPromptSubmit`: the prompt is blocked.
  - `Stop`: Claude does not stop and continues; stderr tells it why.
  - `PostToolUse`: cannot block (the tool already ran); Claude sees stderr.
- Any other code: non-blocking error; the action goes on. **To enforce a policy, use exit 2, never exit 1.**

## JSON output (stdout, exit 0)
- `PreToolUse`:
  `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}`
  `permissionDecision`: `allow` | `deny` | `ask` | `defer`. Optional `updatedInput` (replaces the whole tool input) and `additionalContext`.
- `PostToolUse`, `UserPromptSubmit`, `Stop`: `{"decision": "block", "reason": "..."}`. Context for Claude: `{"hookSpecificOutput": {"hookEventName": "<Event>", "additionalContext": "..."}}`.
- A `Stop` hook that blocks must check `stop_hook_active` to avoid an endless loop.

## Registration (`.claude/settings.json`)
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {"type": "command", "command": "python3", "args": ["${CLAUDE_PROJECT_DIR}/hooks/<hook-name>/hook.py"]}
        ]
      }
    ]
  }
}
```
- With `args`, the command runs without a shell (exec form), so paths with spaces are safe.
- Matcher: `"*"` or omitted = all. `Edit|Write` = exact list. Any other character = unanchored regex (`^Edit$` for a whole-name match).
- Omit `matcher` for events without matcher support (`UserPromptSubmit`, `Stop`).
- `timeout` (seconds) is optional. Default: 600, but 30 for `UserPromptSubmit`.
- `$CLAUDE_PROJECT_DIR` is also set in the hook's environment.
