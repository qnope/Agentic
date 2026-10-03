# Scenario 13: The skill must trigger from its description

## Prompt
Create a skill that adds a security checklist (input validation, authz checks, secrets in code, session handling) to my code review whenever I ask for a review of a change that touches authentication or login code. It must kick in on its own: I never want to have to name the skill.

## Setup
None

## Pass criteria
- [ ] At least one scenario asks for a code review of an auth/login change WITHOUT naming the skill, and its GREEN run does not tell the test agent to read `SKILL.md`: the skill is installed in the run's scratch directory (`.claude/skills/<skill-name>/`) or the test agent gets only the skill's name, description and path, so it must choose the skill from the description.
- [ ] At least one scenario is a negative trigger: a review request for a change with no auth code (for example a CSS change). Its pass criteria say the security checklist is NOT in the output.
- [ ] The action list shows both trigger scenarios were run in GREEN and REFACTOR in the way described in the first item.
- [ ] If a trigger scenario failed in GREEN, the agent changed the `description` frontmatter and re-ran ALL scenarios.
- [ ] The final report has a row for each trigger scenario with its final result.

## RED baseline (without the skill)
2026-10-03 — FAIL (2 of 2 runs). Both runs tested only positive triggers. Both deleted the negative-trigger scenario (review of a non-auth change): "it passes even without the skill, and the creation rules don't allow keeping such tests." Over-triggering was never tested.
