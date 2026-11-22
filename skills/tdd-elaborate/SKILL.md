---
name: tdd-elaborate
description: Turns a feature request into the spec file `specs/<feature>/spec.md` and gets it approved by the human partner. It is the first step of the tdd-loop workflow and writes no code. Use when the user asks to elaborate, specify or start a new feature, or approves a draft spec.
---

# TDD Elaborate

First step of the `tdd-loop` workflow: `tdd-elaborate -> tdd-plan -> tdd-implement`. This step writes the spec and nothing else.

## Rules (no exceptions, even if the human partner asks)
1. **Unclear → ask.** You must be able to write every behavior as "given <input>, the result is <result>", and to name the test command. If you cannot for one point, ask the human partner (see "How to ask") and write no file before the answers. Do this even if the user says not to ask or is in a hurry: a guessed spec gives wrong tests.
2. **Spec only.** Create or change only `specs/<feature>/spec.md`. Write no code, no test, no task file and no `progress.json`, even if the user asks to start coding. Say that the code is written in the step `tdd-implement`.
3. **Only the human partner approves.** Write `Status: approved` only after the human partner said the spec is approved.
4. **Not a feature** (a question, an explanation, a one-line fix) → do not use this skill and create no `specs/` folder.

## How to ask
Every question of rule 1 is multiple-choice: give 2 to 4 options, the answers you find the most likely.

- **Your session has a question tool** that shows the options to pick (`AskUserQuestion` in Claude Code, `AskQuestion` in Cursor, `request_user_input` in Codex): ask every question with it, never in plain text. Call it again if it takes fewer questions than you have, or if an answer leaves a point unclear. When every point is clear, go to Step 1 in the same turn.
- **Your session has no such tool, or the tool gives no answer**: write all your questions at once in this format, and stop.

```
1. <question>
   a) <option>
   b) <option>
```

## Step 1 — Write the draft
`<feature>` is the name the user gave, else a short name you choose. It is kebab-case. Write `specs/<feature>/spec.md` in exactly this format:

```
# Spec: <feature>

Status: draft

## Goal
<1 to 3 sentences: what the feature does>

## Behaviors
- B1: given <input>, the result is <result>.
- B2: given <input>, the result is <result>.

## Out of scope
- <what the feature does not do>, or `None`

## Test command
`<one shell command, run from the project root, that builds and runs all the tests>`
```

One behavior per line. Each one can be checked by one test.

## Step 2 — Ask for the approval
Give the path of the spec, ask "Do you approve this spec?" and stop. Do not go to the next step.

## Step 3 — When the human partner approves
Replace the line `Status: draft` with `Status: approved`. Change no other line and no other file. Say that the next step is `tdd-plan`. If the skill `tdd-plan` is available, continue with it.
