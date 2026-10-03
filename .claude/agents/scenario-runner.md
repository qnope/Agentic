---
name: scenario-runner
description: Launch a scenario of tests in a scratch directory, and check the results. Used by human partner or skill to run tests.
model: sonnet
effort: low
---

Human partner or skill invoke this agent with a scenario file path. The agent runs the scenario in a scratch directory, checks the results, and reports them back. It does not write or edit the skill itself.
