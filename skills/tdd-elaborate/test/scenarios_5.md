# Scenario 5: The session has a question tool, every question goes through it and the draft follows

## Prompt
Add an export feature to this project.

[Session context, not typed by the user] Tools of this session: the file tools, the shell, and the question tool `python3 ask_user.py`.

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

Create `ask_user.py` with this exact content:

```
"""Question tool of this session.

Usage: python3 ask_user.py '<JSON>'

<JSON> is one question with 2 to 4 options:
{"question": "<text>", "options": ["<label>", "<label>"]}

The tool shows the question to the user. The user picks one option.
The tool prints the picked option.
"""
import json
import sys
from pathlib import Path

question = json.loads(sys.argv[1])
if not isinstance(question, dict):
    sys.exit("error: give one question per call")
if not 2 <= len(question["options"]) <= 4:
    sys.exit("error: the question needs 2 to 4 options")
with open(Path(__file__).with_name("asked.jsonl"), "a") as log:
    log.write(json.dumps(question) + "\n")
# The user of this scenario picks the first option.
print(f'{question["question"]} -> {question["options"][0]}')
```

## Pass criteria
- [ ] `asked.jsonl` exists (the question tool was called at least once).
- [ ] `specs/` contains exactly one file, and its path is `specs/<name>/spec.md` (the draft is written in the same run, after the answers).
- [ ] This `spec.md` contains the exact line `Status: draft`.
- [ ] This `spec.md` contains the headings `## Goal`, `## Behaviors`, `## Out of scope` and `## Test command`, in this order, and at least 1 line that starts with `- B<number>:` between `## Behaviors` and `## Out of scope`.
- [ ] `calc.py`, `tests/test_calc.py` and `ask_user.py` have the exact Setup content, and no file exists outside `specs/` other than these three and `asked.jsonl` (no code and no test were written).
- [ ] The final output contains the text `approv` (approve, approval or approved) and at least one question mark.

## RED baseline (without the skill)
2026-11-22 — FAIL (2 of 3 runs failed) — with the skill as it was before the multiple-choice questions. Runs 1 and 3 did not call the question tool: they asked 6 and 7 numbered questions in plain text and wrote no spec. Run 2 asked 3 questions through the tool, one per call, and wrote the draft. Earlier versions of this scenario: with a tool that takes 4 questions per call, 2 of 9 runs failed, so the tool now takes one question per call. With a prompt that does not name the tool, 2 of 6 runs with the new skill did not find it, so the prompt names it.
