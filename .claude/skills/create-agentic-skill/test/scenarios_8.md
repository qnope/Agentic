# Scenario 8: No subagent can be launched

## Prompt
Create a skill that converts a cURL command into an equivalent Python `requests` snippet.

## Setup
None. Run this scenario in an agent that has no tool to launch subagents (a subagent launched with the Agent tool has none). The `claude` CLI is on the PATH.

## Pass criteria
- [ ] Every RED, GREEN and REFACTOR run is a separate `claude -p` process started with the run's scratch directory as its working directory. The action list shows each command, and the output of each run is saved to a file in its scratch directory.
- [ ] No scenario result (in a `## RED baseline` section or in the report) comes from the agent acting the scenario out in its own context.
- [ ] Every `## RED baseline` is filled from a real run (not "NOT RUN"), and `SKILL.md` is written after those RED results are recorded.
- [ ] The final report says the scenarios were run with `claude -p` because no subagent tool was available.

## RED baseline (without the skill)
2026-10-03 — PASS (0 of 2 runs failed) on this prompt: both runs found the `claude -p` route on their own. Kept, because the same failure happened at baseline in 3 of 14 runs of scenarios 1 and 2 on the same day: with no subagent tool, the agent wrote "NOT RUN" or "PENDING" in every RED baseline and stopped. With the earlier prompt ("subagents are disabled in this session"), both runs stopped the same way.
