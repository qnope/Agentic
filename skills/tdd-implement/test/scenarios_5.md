# Scenario 5: Two tasks run at the same time, each in its git worktree, and their merge conflicts

## Prompt
Implement the feature `text-stats`.

## Setup
Copy `mcp-servers/tdd-progress/progress.py` from the repository to the same path in the scratch directory.

Copy `agents/tdd-developer.md` from the repository to the same path in the scratch directory.

Copy `agents/tdd-reviewer.md` from the repository to the same path in the scratch directory.

Copy `agents/tdd-real-tester.md` from the repository to the same path in the scratch directory.

Create `.gitignore` with this exact content:

````
__pycache__/
````

Create `stats.py` with this exact content:

````
import sys

COMMANDS = {}


def main(argv):
    if len(argv) != 3 or argv[1] not in COMMANDS:
        print("usage: stats.py <command> <text>", file=sys.stderr)
        return 2
    print(COMMANDS[argv[1]](argv[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
````

Create `specs/text-stats/spec.md` with this exact content:

````
# Spec: text-stats

Status: approved

## Goal
Add two commands to the program `stats.py`. The command `words` counts the words of a text. The command `vowels` counts the vowels of a text. The program already reads the command line and prints the result of the command that it finds in its table `COMMANDS`.

## Behaviors
- B1: given `python3 stats.py words "the quick fox"`, the result is the line `3` on standard output and the exit code `0`.
- B2: given `python3 stats.py words ""`, the result is the line `0` on standard output and the exit code `0`.
- B3: given `python3 stats.py vowels "Hello World"`, the result is the line `3` on standard output and the exit code `0`.
- B4: given `python3 stats.py vowels "xyz"`, the result is the line `0` on standard output and the exit code `0`.

## Out of scope
- None

## Test command
`python3 -m unittest discover -s tests`
````

Create `specs/text-stats/tasks/T1.md` with this exact content:

````
# T1: Count the words

## Goal
Add the command `words` to `stats.py`: the function `count_words(text)` and its entry `words` in `COMMANDS`. The tests go in the new file `tests/test_words.py`.

## Behaviors
- B1: given `python3 stats.py words "the quick fox"`, the result is the line `3` on standard output and the exit code `0`.
- B2: given `python3 stats.py words ""`, the result is the line `0` on standard output and the exit code `0`.

## Tests to write
- `python3 stats.py words "the quick fox"`: prints `3` and exits with code `0`.
- `python3 stats.py words ""`: prints `0` and exits with code `0`.

## Depends on
None
````

Create `specs/text-stats/tasks/T2.md` with this exact content:

````
# T2: Count the vowels

## Goal
Add the command `vowels` to `stats.py`: the function `count_vowels(text)` and its entry `vowels` in `COMMANDS`. The tests go in the new file `tests/test_vowels.py`.

## Behaviors
- B3: given `python3 stats.py vowels "Hello World"`, the result is the line `3` on standard output and the exit code `0`.
- B4: given `python3 stats.py vowels "xyz"`, the result is the line `0` on standard output and the exit code `0`.

## Tests to write
- `python3 stats.py vowels "Hello World"`: prints `3` and exits with code `0`.
- `python3 stats.py vowels "xyz"`: prints `0` and exits with code `0`.

## Depends on
None
````

Create `specs/text-stats/progress.json` with this exact content:

````
{
  "feature": "text-stats",
  "status": "open",
  "test_command": "python3 -m unittest discover -s tests",
  "tasks": [
    {
      "id": "T1",
      "title": "Count the words",
      "file": "tasks/T1.md",
      "depends_on": [],
      "status": "new",
      "rejections": 0,
      "note": ""
    },
    {
      "id": "T2",
      "title": "Count the vowels",
      "file": "tasks/T2.md",
      "depends_on": [],
      "status": "new",
      "rejections": 0,
      "note": ""
    }
  ]
}
````

Then run these commands in the scratch directory, in this order (the scratch directory becomes a git repository with one commit; the folder `specs/` is not in the commit, like a spec written after the last commit):

````
git init --quiet --initial-branch main
git config user.name Test
git config user.email test@example.com
git config commit.gpgsign false
git add .gitignore agents mcp-servers stats.py
git commit --quiet -m base
````

## Pass criteria
All the commands run from the scratch directory root.

- [ ] `python3 mcp-servers/tdd-progress/progress.py status text-stats` exits with code 0 and its output contains `2 of 2 tasks done`.
- [ ] `git log --format=%s` prints exactly 4 lines: `text-stats: closed`, then `text-stats T1: Count the words` and `text-stats T2: Count the vowels`, in any order, then `base` (each task is one commit: the merge of its worktree and its progress are in the same commit).
- [ ] `git reflog` prints exactly 2 lines that contain `Fast-forward` (each task came from its own worktree: the tool gives a worktree to a task only while the other task is ready or in progress).
- [ ] `git status --porcelain`, run before any other check, prints nothing, and `git branch --show-current` prints `feature/text-stats` (no work was left uncommitted in the project root).
- [ ] `git worktree list` prints exactly 1 line, `git branch --list 'tdd/*'` prints nothing, and the folder `.worktrees` does not exist (the tool removed the worktrees).
- [ ] `python3 -m unittest discover -s tests` exits with code 0 and prints `Ran <n> tests` with n at least 4.
- [ ] `python3 stats.py words "the quick fox"` prints exactly the line `3` and exits with code 0, and `python3 stats.py vowels "Hello World"` prints exactly the line `3` and exits with code 0 (the merge kept both commands).
- [ ] In `specs/text-stats/progress.json`, the `review` of `T1` and of `T2` each start with `APPROVED`, the `real_testing` of `T1` and of `T2` each start with `PASSED`, and no task has a field `worktree`.
- [ ] In `specs/text-stats/progress.json`, `T1` or `T2` has `rejections` at 1 or more and a `note` that contains `merge conflict` (the tool sent the conflict back to the developer, and the task then went to `done` through a new review and a new real test).
- [ ] The folders `specs/text-stats/real-testing/T1/` and `specs/text-stats/real-testing/T2/` each contain at least one file.
- [ ] `specs/text-stats/spec.md`, `specs/text-stats/tasks/T1.md` and `specs/text-stats/tasks/T2.md` have the exact Setup content.
- [ ] The final output has a line that contains `T1`, `APPROVED` and `PASSED`, and a line that contains `T2`, `APPROVED` and `PASSED`.

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — baseline with the skill as it was before the parallel mode. The 3 runs took one task at a time. The tool gave `T1` a worktree, but the runs developed `T1` in the project root: the tool refused `done`, and they copied the files into the worktree by hand ("The skill does not mention that the tool creates a git worktree"). `T2` then ran alone, got no worktree, and its work stayed uncommitted in the project root (`stats.py` modified, `tests/test_vowels.py` untracked). One `Fast-forward` instead of two, and no merge conflict went back to a developer.
