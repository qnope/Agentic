# Scenario 4: The real test finds a defect that the unit tests miss

## Prompt
Continue the feature `greet`.

## Setup
Copy `mcp-servers/tdd-progress/progress.py` from the repository to the same path in the scratch directory.

Copy `agents/tdd-developer.md` from the repository to the same path in the scratch directory.

Copy `agents/tdd-reviewer.md` from the repository to the same path in the scratch directory.

Copy `agents/tdd-real-tester.md` from the repository to the same path in the scratch directory.

Create `specs/greet/spec.md` with this exact content:

````
# Spec: greet

Status: approved

## Goal
Add a program `greet.py`. It prints a greeting for the name given on the command line.

## Behaviors
- B1: given `python3 greet.py Ada`, the result is the line `Hello, Ada!` on standard output and the exit code `0`.
- B2: given `python3 greet.py` with no name, the result is the line `usage: greet.py <name>` on standard error and the exit code `2`.

## Out of scope
- None

## Test command
`python3 -m unittest discover -s tests`
````

Create `specs/greet/tasks/T1.md` with this exact content:

````
# T1: Greeting program

## Goal
Add the program `greet.py`. It prints `Hello, <name>!` for the name given on the command line.

## Behaviors
- B1: given `python3 greet.py Ada`, the result is the line `Hello, Ada!` on standard output and the exit code `0`.
- B2: given `python3 greet.py` with no name, the result is the line `usage: greet.py <name>` on standard error and the exit code `2`.

## Tests to write
- `python3 greet.py Ada`: prints `Hello, Ada!` and exits with code `0`.
- `python3 greet.py` with no name: prints `usage: greet.py <name>` on standard error and exits with code `2`.

## Depends on
None
````

Create `specs/greet/progress.json` with this exact content:

````
{
  "feature": "greet",
  "status": "open",
  "test_command": "python3 -m unittest discover -s tests",
  "tasks": [
    {
      "id": "T1",
      "title": "Greeting program",
      "file": "tasks/T1.md",
      "depends_on": [],
      "status": "real-testing",
      "rejections": 0,
      "note": "",
      "review": "APPROVED\n- test_greeting_names_the_person\n- test_no_name_returns_exit_code_2"
    }
  ]
}
````

Create `greet.py` with this exact content:

````
import sys


def greeting(name):
    return f"Hello, {name}!"


def main(argv):
    if len(argv) < 2:
        print("usage: greet.py <name>", file=sys.stderr)
        return 2
    print(greeting(argv[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
````

Create `tests/test_greet.py` with this exact content:

````
import unittest

import greet


class GreetTest(unittest.TestCase):
    def test_greeting_names_the_person(self):
        self.assertEqual(greet.greeting("Ada"), "Hello, Ada!")

    def test_no_name_returns_exit_code_2(self):
        self.assertEqual(greet.main(["greet.py"]), 2)
````

## Pass criteria
- [ ] `python3 greet.py Ada`, run from the scratch directory root, prints exactly the line `Hello, Ada!` on standard output and exits with code 0.
- [ ] `python3 greet.py`, run from the scratch directory root, exits with code 2 and prints `usage: greet.py <name>` on standard error.
- [ ] `python3 -m unittest discover -s tests`, run from the scratch directory root, exits with code 0.
- [ ] `python3 mcp-servers/tdd-progress/progress.py status greet` exits with code 0 and its output shows 1 task under `done` and 0 task under `new`, `dev`, `review` and `real-testing`.
- [ ] In `specs/greet/progress.json`, `T1` has `rejections` at 1 or more and its `note` is not empty (the real test sent the task back to dev with remarks: the defect was not fixed in silence).
- [ ] In `specs/greet/progress.json`, the `real_testing` of `T1` starts with `PASSED` and contains `B1` and `B2`.
- [ ] `specs/greet/progress.json` is byte-identical to its own content written again with `json.dumps(data, indent=2) + "\n"` (this is the layout the tool writes).
- [ ] `specs/greet/spec.md` and `specs/greet/tasks/T1.md` have the exact Setup content.

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — the 3 runs did the real test, saw `Hello, greet.py!` and sent `T1` back to `dev` with the remarks. Then they stopped: no developer fix, no new review, no new real test. `greet.py` still printed `Hello, greet.py!` and `T1` stayed in `dev`. Run 3 stored a wrong remark ("the note I stored with the move to dev wrongly says that B2 fails").
