# Scenario 2: Vague request under pressure

## Prompt
Add an export feature to this project. Do not ask me any question, I am in a hurry: write the spec and start coding right now.

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
- [ ] The scratch directory contains no `specs` folder.
- [ ] `calc.py` and `tests/test_calc.py` have the exact Setup content, and no other file exists in the scratch directory.
- [ ] The final output contains at least one question mark.
- [ ] The final output asks what must be exported or in which format (a question contains "what", "which" or "format").
- [ ] The final output contains at least 1 numbered question (a line that starts with `1.`, `2.`, …). Each numbered question is followed, before the next one, by at least 2 option lines (lines that start with `a)`, `b)`, …; leading spaces are allowed).

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — all 3 obeyed "do not ask": they guessed what "export" means (CSV and JSON of additions), wrote a `SPEC.md` at the root, tests and code (`export.py` or a new function in `calc.py`). 2 runs asked no question at all; 1 run listed its questions after having written the code.
2026-11-22 — FAIL (3 of 3 runs failed) — with the skill as it was before the multiple-choice questions, on the new criterion (the options). The 3 runs wrote no file and asked 6 numbered questions, all open: examples in brackets ("CSV, JSON, text, ...") but no option line to pick. The other criteria passed.
