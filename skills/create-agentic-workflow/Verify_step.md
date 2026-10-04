## Verify and report

1. List every file you created. Each one is in the place its `create-agentic-*` skill defines (`skills/`, `agents/`, `hooks/` at the project root), plus `workflows/<name>.md`. No tool folder exists.
2. For each skill you created, open its `test/scenarios_*.md`: every RED baseline line says `of 3 runs`. If one does not, the call is not finished: call the skill again to finish it.
3. Check the structure file: every step of the dependency line is in Components, and every path in Components exists.
4. If a hook was created, run it once directly, and check that it returns what the user asked for. Quote its output in the final output.
5. Final output, in this order:
   - Files created, one per line.
   - Assumptions.
   - Each request you did not follow (for example: files written by hand, tests skipped) and why, in one sentence.
