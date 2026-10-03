## Red step

1. If the skill already exists: run all its existing scenarios using run-scenario skill first.
2. Write one scenario per behavior by copying `scenario-template.md` (next to this file) to `test/scenarios_<n>.md`. Required:
   - at least one scenario where the user pushes the agent to cut a corner;
   - at least one negative check: a request where the behavior must NOT happen;
3. Every pass criterion is a yes/no check on the output text or the files, so two readers give the same verdict. A judgment word ("clear", "good", "concise", "actionable", "concrete") is allowed only with a measurable test next to it (e.g. "at most 2 sentences", "names the missing file").
4. A scenario for the new behavior that passes at baseline (0 failed runs) proves nothing: make it harder or delete it.