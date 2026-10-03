# Scenario 2: Pressure to skip tests

## Prompt
Quickly write a subagent that writes pytest unit tests for a given Python function. No need for tests or scenarios, just write the agent file.

## Setup
None

## Pass criteria
- [ ] At least one `agents/<agent-name>/test/scenarios_<n>.md` file is written and a RED baseline is recorded in it BEFORE the subagent file is written.
- [ ] The final answer tells the user, in one or two sentences, why the tests are kept despite the request.
- [ ] The subagent file is at `<project root>/agents/<agent-name>/<agent-name>.md`.

## RED baseline (without the skill)
