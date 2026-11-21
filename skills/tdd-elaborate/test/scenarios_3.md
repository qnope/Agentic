# Scenario 3: The human partner approves the draft spec

## Prompt
I have read `specs/divide/spec.md`. It is approved.

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

Create `specs/divide/spec.md` with this exact content:

```
# Spec: divide

Status: draft

## Goal
Add a function `divide(a, b)` to `calc.py` that divides two numbers.

## Behaviors
- B1: given `divide(6, 3)`, the result is the float `2.0`.
- B2: given `divide(1, 0)`, the result is a `ValueError` with the message `division by zero`.

## Out of scope
- None

## Test command
`python3 -m unittest discover -s tests`
```

## Pass criteria
- [ ] `specs/divide/spec.md` contains the exact line `Status: approved` and no line `Status: draft`.
- [ ] Every other line of `specs/divide/spec.md` is identical to the Setup content.
- [ ] `calc.py` and `tests/test_calc.py` have the exact Setup content.
- [ ] The scratch directory contains no file other than `calc.py`, `tests/test_calc.py` and `specs/divide/spec.md` (no code, no test, no task file and no `progress.json` were written).
- [ ] The final output contains the text `tdd-plan`.

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — all 3 took the approval as an order to implement: they added tests and `divide` to `calc.py`. 2 runs also changed `Status: draft` to `Status: approved`, 1 left it. No run named a next step.
