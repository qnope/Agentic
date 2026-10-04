---
name: create-agentic-agent
description: Creates an agent (subagent) as one simple, tool-agnostic markdown file in `agents/`. Use when the user asks to create, write or add an agent or subagent definition.
---

# Create Agentic Agent

An agent is one markdown file: a short header and a prompt. It must work in any LLM tool, so it contains no tool-specific syntax.

## Rules
1. **Purpose unclear → ask.** If the request does not say what the agent must do, ask "What must the agent do?" and write no file. Do this even if the user says not to ask.
2. **Never overwrite.** Before writing, check in a separate step (a different command, run first) whether `agents/<name>.md` exists. Never check and write in the same command. If it exists, change nothing, say the file exists, and ask: overwrite or another name?
3. **Tool-agnostic only.** Do not add `tools`, `model` or any other key. Do not use `@` mentions. Do not name tools or products (no "Bash", "Grep", product names). Write generic verbs: open, search, run a command. If the user asks for such fields, do not add them. In the final output, name each omitted field and say it belongs in the tool's own agent config.
4. **Location.** Write only `agents/<name>.md` at the project root. Do not create tool folders such as `.claude` or `.cursor`.
5. **Size.** The file is at most 3 KiB (3072 bytes). Check the size after writing. If the source material does not fit, shorten it (keep the key points) even if the user asks to copy it verbatim. In the final output, say the content was shortened and name the 3 KiB limit.
6. **Not an agent request** (a question, code, a skill) → do not use this skill and create no file.

## File format
Name: kebab-case. `name` equals the file name without `.md`.

```
---
name: <kebab-case-name>
description: <one line: what the agent does. Use when <trigger>.>
---
<One sentence: the role.>

## Steps
1. <imperative step>
2. <imperative step>

## Output
<exact format of the reply>
```

- Frontmatter has exactly two keys: `name` and `description`.
- `description` is one line and contains "Use when".
- The body is at most 60 lines.
