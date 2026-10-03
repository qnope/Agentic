---
name: run-scenario
description: Launch a scenario of tests in a scratch directory, and check the results. Used by human partner or skill to run tests.
model: sonnet
effort: low
---

Skill to run a scenario 3 times in scratch directory, check the results, and report them back.

** Not write or edit the skill itself **
** Always remove the scratch directory after the run, even if the run fails. **
** Run it 3 times, even if the first run passes. **

## How to run a scenario

Read the scenario file and create a scratch directory. The scratch directory is a temporary project root for the scenario run. It is deleted after the run.

1. Create 3 scratch directories, e.g. `mktemp -d /tmp/claude-scenario-1-XXXXXX`.
2. Create the scenario's `## Setup` files in all the 
scratch directories. Create every file it lists with the content it specifies. Do not create any files if the scenario does not have a `## Setup` section.
3. Give the scenario's `## Prompt`, the skill (if it exists) and the path to the scratch directory as the user request to @scenario-runner agent. You can also give the path to the skill to the agent, so it can use the skill's templates and scripts. The agent runs the scenario in the scratch directory, checks the results, and reports them back. It does not write or edit the skill itself.
4. When all agents finished, check the `## Pass criteria` items against the files in all the scratch directories. Output "GREEN" if all pass, "RED" if any fail. If RED, output all the failed criteria.
5. Remove all scratch directories, even if the run fails.
