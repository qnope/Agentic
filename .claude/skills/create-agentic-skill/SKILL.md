---
name: create-agentic-skill
description: Creates or changes a skill with Red-Green-Refactor - test scenarios in test/scenarios_<n>.md first, then the minimal SKILL.md, then cleanup - and re-runs all scenarios after every change. Use when the user asks to create a new skill or change an existing one.
---

# Create Agentic Skill

Every skill is built test-first. Tests are scenario files kept in the skill folder so they can be re-run on every future change.

New skills go in `skills/<skill-name>/` at the project root (NOT `.claude/skills/`), so they are easy to export:
```
skills/<skill-name>/
├── SKILL.md
├── <supporting files, if any>
└── test/
    ├── scenarios_1.md
    └── scenarios_2.md ...
```

## Rules (no exceptions, even if the user asks)
- "The skill" means every file in the skill folder except `test/` (`SKILL.md`, templates, scripts, references). The rules below apply to all of them.
- Never write or edit the skill before the RED step is done and recorded.
- Before any change to an existing skill, run ALL its scenarios. After any change, run ALL scenarios again.
- When the user asks to cut a corner (skip tests, skip old tests, skip RED, edit first and test later, fewer than 3 runs per scenario, "it is only a one-line change" or "only a supporting file"), do it the test-first way anyway. In the final answer, tell the user why in one or two sentences (no more), naming the corner they asked to cut. Reasons: RED first proves the test can catch the problem; re-running old scenarios proves nothing else broke; every file of the skill changes its behavior; 3 runs catch a behavior that fails only some of the time, and a lower effort makes that more likely, not less.
- Never overwrite an existing `test/scenarios_<n>.md` with a different scenario. A new scenario takes the next free number.
- Never write the result of a regression re-run into an existing scenario file: give it in the report. An existing scenario file changes only in the case below.
- If the request contradicts the pass criteria of an existing scenario, change those criteria in the same file (do not delete it, do not add a second scenario that repeats it). Add a dated line under its `## RED baseline` that says what changed and why, run it RED again with the old skill (new runs; old outputs re-graded do not count), and say in the final report which scenario was changed and why. Do not stop to ask: the request is the permission.
- A result comes only from a real isolated run (see "How to run a scenario"). Never act a scenario out in your own context, and never record a result the user reports.

## Step 1 — Clarify
1. List `.claude/skills/` and `skills/`. If an existing skill already does the job or triggers on the same requests, and the user did not name it: ask whether to change that skill or create a separate one, naming its path. Then stop. Write no file.
2. Can you state in one sentence what the skill does?
   - **No** (e.g. "a skill for testing": testing what, how?): ask the user what it does, when it triggers, and what it outputs. Then stop. Write no file and no draft. This holds even if the user says "don't ask, just make it": tell them in one sentence that the skill cannot be built without these answers (e.g. "The skill cannot be built without these answers."). If you cannot reach the user, put the questions in your final answer and stop.
   - **Yes**: do not ask. Choose sensible defaults for the trigger and the output, list them as "Assumptions" in the final report, and continue.

Skill name: kebab-case. Location of a new skill: `skills/<skill-name>/` at the project root. An existing skill is changed where it already is.

## Step 2 — RED
1. If the skill already exists: run all its existing scenarios first, unchanged, with the current skill, before writing or editing any file in the skill folder, `test/` included. They are the regression baseline. If one already fails, say so in the report.
2. Write one scenario per behavior by copying `scenario-template.md` (next to this file) to `test/scenarios_<n>.md`. Required:
   - at least one scenario where the user pushes the agent to cut a corner;
   - at least one negative check: a request where the behavior must NOT happen;
   - for a skill that must trigger on its own: one trigger scenario that must use the skill and one that must not (see "How to run a scenario", trigger runs).
3. Every pass criterion is a yes/no check on the output text or the files, so two readers give the same verdict. A judgment word ("clear", "good", "concise", "actionable", "concrete") is allowed only with a measurable test next to it (e.g. "at most 2 sentences", "names the missing file"). Every scenario writes its concrete inputs as literal strings in `## Prompt` or `## Setup` (a file in `## Setup` has its exact contents written out).
4. Run each new scenario WITHOUT the new behavior (see "How to run a scenario").
5. Write the result in each new scenario's `## RED baseline` section: date, how many runs failed (e.g. "FAIL (3 of 3 runs)"), and what the agent did wrong. Every new scenario gets a result; "not applicable" is not one.
6. A scenario for the new behavior that passes at baseline (0 failed runs) proves nothing: make it harder or delete it. A negative check or a check of behavior that already exists is kept: write "PASS at baseline, kept as a regression check".

## Step 3 — GREEN
1. Write the minimal skill that fixes the recorded failures, nothing more. Frontmatter: `name` (equal to the folder name) and `description` (what it does, then "Use when ..."). The description decides when the skill triggers.
2. Run ALL scenarios WITH the skill.
3. If any fails, fix the skill and run ALL scenarios again. Repeat until all pass. If a trigger scenario fails, fix `description`.

## Step 4 — REFACTOR
1. Remove text that no scenario needs. Close any loophole the runs revealed.
2. Run ALL scenarios again, even if nothing was removed. All must pass.

## Step 5 — Report
- Files created or changed (and any scenario whose criteria were changed, with why).
- Table: scenario | RED result | final result, each as a count (e.g. 3/3 passed).
- Assumptions, if any.
- How the scenarios were run (subagents or `claude -p`, and why, e.g. "`claude -p`, because no subagent tool was available"), the effort level if one was set, and where the scratch directories are.
- For a new skill: it is in `skills/<skill-name>/`; to use it in Claude Code, copy or symlink it into `.claude/skills/`.

## How to run a scenario
One run of a scenario = 3 independent runs, in parallel, each in its own fresh scratch directory. The scenario passes only if all 3 pass. At RED, it fails if at least 1 fails.

1. Create a fresh scratch directory per run: in the session scratchpad if one exists, otherwise in `<project>/.scratch/`. Never inside the skill folder or on real project files. Apply the scenario's `## Setup` there.
2. Build the test prompt:
   - the scenario's `## Prompt` as the user request,
   - RED for a new skill: nothing more. RED for an existing skill: copy the whole old skill folder (without `test/`) to the scratch directory and add "Read and follow `<copy>/SKILL.md` first.",
   - GREEN/REFACTOR: "Read and follow `<path>/SKILL.md` first.",
   - trigger runs (GREEN/REFACTOR) do not say to read the skill: install a copy of the skill in `<scratch>/.claude/skills/<skill-name>/` (with `claude -p`), or add only "Available skill: `<name>`: `<description>`. File: `<path>/SKILL.md`. Use it only if it fits the request.",
   - always: "You cannot talk to the user. If you need to ask something, put the questions in your final answer and stop. End with an ordered list of every action you took."
3. Launch it:
   - if the user names an effort level (e.g. "low effort"): every run, RED, GREEN and REFACTOR, is a `claude -p` process (command below) with `--effort <level>` added. A subagent cannot set an effort level, so do not use one. Keep 3 runs per scenario;
   - otherwise, with a subagent tool: a `general-purpose` subagent, with the scratch directory as its project root. Do not pass `--effort`;
   - without one (e.g. you are a subagent yourself): a separate process, from the scratch directory: `cd <scratch> && claude -p "<test prompt>" --add-dir <skill folder> --allowedTools "<tools the scenario needs>" < /dev/null > _run-output.txt 2>&1`. Never pass `--dangerously-skip-permissions`. Never reuse or delete a run directory: its output is the evidence;
   - if neither is possible: write "NOT RUN" and the reason under `## RED baseline`, write no skill, and tell the user what is needed. Then stop.
4. Check every `## Pass criteria` item against the files in the scratch directory first, then the action list. Files beat claims: a claim the files do not support fails. The run passes only if every item passes.
