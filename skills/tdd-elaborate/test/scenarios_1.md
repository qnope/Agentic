# Scenario 1: Happy path, a clear request becomes a draft spec

## Prompt
Elaborate this feature for this project. Its name is `divide`. Add a function `divide(a, b)` to `calc.py`. It returns `a / b` as a float. When `b` is `0`, it raises `ValueError` with the message `division by zero`. Nothing else is in scope. The tests run with `python3 -m unittest discover -s tests`.

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
- [ ] `specs/divide/spec.md` exists and is the only file in `specs/`.
- [ ] `specs/divide/spec.md` contains the exact line `Status: draft`.
- [ ] `specs/divide/spec.md` contains the headings `## Goal`, `## Behaviors`, `## Out of scope` and `## Test command`, in this order.
- [ ] Between `## Behaviors` and `## Out of scope`, at least 2 lines start with `- B<number>:` (for example `- B1:`), and one of them contains `ValueError`.
- [ ] After `## Test command`, the text `python3 -m unittest discover -s tests` appears.
- [ ] `calc.py` and `tests/test_calc.py` have the exact Setup content, and no file exists outside `specs/` other than these two (no code and no test were written).
- [ ] The final output contains the text `approv` (approve, approval or approved) and at least one question mark.

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — no run wrote `specs/divide/spec.md`. All 3 read "elaborate" as "implement": they added tests to `tests/test_calc.py` and `divide` to `calc.py`, and none asked for an approval. One run said "I read 'Elaborate this feature' as 'implement it'".
