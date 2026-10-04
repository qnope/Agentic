# Scenario 1: Happy path, elaborate -> plan -> implement with a unit test gate hook

## Prompt
Create a workflow named `feature-flow` for this Python project. It has three steps, in this order: `elaborate` (turns a feature request into a spec), `plan` (turns the spec into an ordered task list), `implement` (writes the code and the unit tests from the plan). The `implement` step must be gated by a hook. The hook runs the unit tests with `python3 -m unittest discover -s tests`. It returns `{}` when all tests pass, otherwise it returns the failed test(s). Do not run the workflow, only create what it needs. When you are done, run the hook yourself once, directly, on this project and quote its output.

## Setup
Create `calc.py` with this exact content:

```
def add(a, b):
    return a + b
```

Create `tests/test_calc.py` with this exact content:

```
import unittest

from calc import add


class AddTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)
```

## Pass criteria
- [ ] `workflows/feature-flow.md` exists and is the only file in `workflows/`.
- [ ] `workflows/feature-flow.md` contains the exact text `elaborate -> plan -> implement`.
- [ ] `skills/` contains exactly the 3 folders `elaborate`, `plan` and `implement`. Each has a `SKILL.md` of at most 8192 bytes, with a line `name: <folder name>` and a `description:` line containing `Use when`.
- [ ] In each of the 3 skills, `test/` contains between 1 and 5 files named `scenarios_*.md`, and each of them has a line that starts with a date (`20` + `YY-MM-DD`, for example `2026-10-04`) and contains the text `of 3 runs`: the RED baseline was recorded with the 3 runs that create-agentic-skill requires.
- [ ] Exactly one non-test `.py` file exists directly in `hooks/`, it has at most 40 lines, a file `hooks/test_*.py` exists, and `python3 -m unittest discover -s hooks` exits with code 0.
- [ ] With the Setup files only, `echo '{}' | python3 hooks/<file>.py` run from the scratch directory root exits with code 0 and its standard output, trimmed, is exactly `{}`.
- [ ] After creating `tests/test_broken.py` (content below), `echo '{}' | python3 hooks/<file>.py` exits with code 2 and its standard output plus standard error contains `test_always_fails`. The file is removed afterwards.
- [ ] `workflows/feature-flow.md` contains the text `hooks/<file>.py` (the gate is recorded).
- [ ] `calc.py` and `tests/test_calc.py` still have the exact Setup content, and the scratch directory contains no `agents`, `.claude`, `.cursor` or `.codex` folder.
- [ ] The final output contains the text `{}` (the hook was run by the agent and its output quoted).

Content of `tests/test_broken.py` for the failing check:

```
import unittest


class BrokenTest(unittest.TestCase):
    def test_always_fails(self):
        self.fail("boom")
```

## RED baseline (without the skill)
2026-10-04 — FAIL (3 of 3 runs failed) — no run wrote `workflows/feature-flow.md` or any `skills/` folder: all 3 invented their own layout (`workflows/feature-flow/` with one markdown file per step) and wrote no `test/` scenarios for the steps. Hooks: runs 1 and 2 wrote a hook with no `hooks/test_*.py` (run 1 also registered it in `.claude/settings.json`); run 3 wrote `hooks/tests_gate.py` and `hooks/test_tests_gate.py` after reading create-agentic-hook. All 3 hooks printed `{}` on the passing project, so the hook criteria alone do not separate the runs. Each run said it used no skill because none creates a workflow. Criterion 4 gained the text `of 3 runs` after the first GREEN passes: one run met every other criterion but recorded its baselines with 1 or 2 runs ("run 3 not made"), and its own report admitted fewer runs than the called skills require. The no-skill baseline runs wrote no skills at all, so they fail this criterion either way.
