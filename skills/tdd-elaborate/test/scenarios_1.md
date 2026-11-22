# Scenario 1: Happy path, a clear request becomes a draft spec, with behaviors of the feature only

## Prompt
Elaborate this feature for this project. Its name is `divide`. Add a function `divide(a, b)` to `calc.py`. It returns `a / b` as a float. When `b` is `0`, it raises `ValueError` with the message `division by zero`. Like every function of the project, it has a docstring and type hints, and its tests go in `tests/test_calc.py`. The `Makefile` target `test` must run the tests. Nothing else is in scope. The tests run with `python3 -m unittest discover -s tests`.

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
- [ ] Between `## Behaviors` and `## Out of scope`, no line contains one of these texts, in any letter case: `docstring`, `type hint`, `makefile`, `make test`, `tests/test_calc.py` (a convention, the place of the tests and the build system are not behaviors).
- [ ] `specs/divide/spec.md` contains the texts `docstring` and `Makefile` (what the request says about them is kept, outside the behaviors).
- [ ] After `## Test command`, the text `python3 -m unittest discover -s tests` appears.
- [ ] `calc.py` and `tests/test_calc.py` have the exact Setup content, and no file exists outside `specs/` other than these two (no code and no test were written).
- [ ] The final output contains the text `approv` (approve, approval or approved) and at least one question mark.

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — no run wrote `specs/divide/spec.md`. All 3 read "elaborate" as "implement": they added tests to `tests/test_calc.py` and `divide` to `calc.py`, and none asked for an approval. One run said "I read 'Elaborate this feature' as 'implement it'".
2026-11-22 — FAIL (3 of 3 runs failed) — with the skill as it was before the rule on the behaviors of the feature only, on the new request (a docstring and type hints, the place of the tests, the `Makefile` target). The 3 runs wrote them as behaviors: "B4: given the function `divide` in `calc.py`, the result is that it has a docstring and type hints", "B5: given the tests of `divide`, the result is that they are in `tests/test_calc.py`", "B6: given the command `make test`, the result is that it runs the tests". The other criteria passed, except in run 1, whose final output was lost by the test session.
