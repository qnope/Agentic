# Scenario 3: Hook that checks that the unit tests pass

## Prompt
Create a hook that checks the unit tests before the agent stops. The hook runs `python3 -m unittest discover -s tests`. It returns `{}` when all tests pass, otherwise it returns the failed test(s).

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
- [ ] Exactly one non-test `.py` file exists directly in `hooks/` at the scratch directory root, it has at most 40 lines and contains the text `unittest`.
- [ ] With the Setup files only, `echo '{}' | python3 hooks/<file>.py` run from the scratch directory root exits with code 0 and its standard output, trimmed, is exactly `{}`.
- [ ] After creating `tests/test_broken.py` (content below), `echo '{}' | python3 hooks/<file>.py` exits with code 2 and its standard output plus standard error contains `test_always_fails`.
- [ ] With `tests/test_broken.py` still in place, `echo '{"stop_hook_active": true}' | python3 hooks/<file>.py` exits with code 0. The file is removed afterwards.
- [ ] A test file `hooks/test_*.py` exists, its text contains `stop_hook_active`, and `python3 -m unittest discover -s hooks` exits with code 0 and prints `Ran 3 tests` or more (any number from 3).
- [ ] The scratch directory contains no `.claude`, `.cursor` or `.codex` directory.

Content of `tests/test_broken.py` for the failing checks:

```
import unittest


class BrokenTest(unittest.TestCase):
    def test_always_fails(self):
        self.fail("boom")
```

## RED baseline (without the skill)
2026-10-04 — FAIL (2 of 3 runs failed) — run against the current skill, which only covers "block while a command is running" (this scenario was added when the skill was extended). Runs 1 and 3 turned the template's `running` into a test runner but dropped the requested `{}`: on a passing project their standard output was empty (run 3: "It does not print `{}`. The skill's contract replaces that"). Run 2 printed `{}` on success and passed. All 3 kept exit code 2 and wrote their unit tests.
