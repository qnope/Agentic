#!/usr/bin/env python3
"""Deterministic progress tracking for the tdd-loop workflow. Standard library only.

One feature = one folder `specs/<feature>/` holding `spec.md`, `tasks/` and `progress.json`.
A task goes new -> dev -> review -> real-testing -> done. A review or a real test can send it back to dev.
In a git repository, a feature gets its own branch, each done task is one commit, and `pr` opens the pull request.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

NEXT = {"new": ("dev",), "dev": ("review",), "review": ("real-testing", "dev"),
        "real-testing": ("done", "dev"), "done": ()}
# A forward move out of a checking status needs the output of its agent: (first line, field that keeps it).
PROOF = {"real-testing": ("APPROVED", "review"), "done": ("PASSED", "real_testing")}
MAX_REJECTIONS = 3
NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")


class ProgressError(Exception):
    """A refused operation. The message says why."""


def run_tests(command, cwd):
    """Run the test command once. Return (exit code, output)."""
    done = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    return done.returncode, (done.stdout + done.stderr).strip()


def _file(root, feature):
    if not isinstance(feature, str) or not NAME.fullmatch(feature):
        raise ProgressError(f"feature name {feature!r} is not kebab-case (example: user-login)")
    return Path(root) / "specs" / feature / "progress.json"


def _load(root, feature):
    path = _file(root, feature)
    if not path.exists():
        raise ProgressError(f"no progress file for feature '{feature}': create it first")
    return json.loads(path.read_text())


def _save(root, data):
    path = _file(root, data["feature"])
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    os.replace(temporary, path)


def _task(data, task_id):
    for task in data["tasks"]:
        if task["id"] == task_id:
            return task
    raise ProgressError(f"unknown task '{task_id}' in feature '{data['feature']}'")


def _unfinished_dependencies(data, task):
    return [d for d in task["depends_on"] if _task(data, d)["status"] != "done"]


def _escalated(task):
    return task["status"] == "dev" and task["rejections"] >= MAX_REJECTIONS


def _check_no_cycle(tasks):
    """Remove the tasks whose dependencies are all removed, until none can be removed."""
    left = {t["id"]: set(t["depends_on"]) for t in tasks}
    while True:
        free = [i for i, needs in left.items() if not needs & left.keys()]
        if not free:
            break
        for task_id in free:
            del left[task_id]
    if left:
        raise ProgressError(f"dependency cycle between tasks: {', '.join(sorted(left))}")


def _run(command, cwd):
    """Run one command with no shell and no input. Return (exit code, output)."""
    try:
        done = subprocess.run(command, cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                              env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    except OSError as error:
        return 1, str(error)
    return done.returncode, (done.stdout if done.returncode == 0 else done.stdout + done.stderr).strip()


def _git(root, *arguments):
    return _run(["git", *arguments], root)


def _branch(root):
    """Return the current branch, or "" when the project root is not the top folder of a git repository."""
    if _git(root, "rev-parse", "--is-inside-work-tree", "--show-cdup") != (0, "true"):
        return ""
    code, branch = _git(root, "symbolic-ref", "--short", "HEAD")
    return branch if code == 0 else ""


def _start_branch(root, feature):
    """On the default branch, create the branch `feature/<feature>` and switch to it."""
    code, default = _git(root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if _branch(root) in ([default.removeprefix("origin/")] if code == 0 else ["main", "master"]):
        code, output = _git(root, "checkout", "--quiet", "-b", f"feature/{feature}")
        if code != 0:
            raise ProgressError(f"cannot create the branch 'feature/{feature}': {output}")


def _commit(root, message, path):
    """Commit the changes under `path`. Return the short hash, or "" with no git repository or no change."""
    if not _branch(root) or not _git(root, "status", "--porcelain", "--", path)[1]:
        return ""
    _git(root, "add", "--all", "--", path)
    code, output = _git(root, "commit", "--quiet", "--message", message, "--", path)
    if code != 0:
        raise ProgressError(f"the commit failed: {output}")
    return _git(root, "rev-parse", "--short", "HEAD")[1]


def _record(root, data, message, path="."):
    """Save the progress file, then commit the changes under `path`. A failed commit restores the file."""
    file = _file(root, data["feature"])
    before = file.read_text()
    _save(root, data)
    try:
        return _commit(root, message, path)
    except ProgressError:
        file.write_text(before)
        raise


def create(root, feature, test_command, tasks):
    """Write `specs/<feature>/progress.json` with every task in status new."""
    path = _file(root, feature)
    if not isinstance(test_command, str) or not test_command.strip():
        raise ProgressError("the test command is empty")
    if not tasks:
        raise ProgressError("a feature needs at least one task")
    if path.exists():
        old = json.loads(path.read_text())
        if old["status"] == "closed":
            raise ProgressError(f"feature '{feature}' is closed: use another feature name")
        if any(t["status"] != "new" for t in old["tasks"]):
            raise ProgressError(f"feature '{feature}' has already started: it cannot be planned again")
    entries = []
    for task in tasks:
        task_id, title = str(task.get("id", "")).strip(), str(task.get("title", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]+", task_id):
            raise ProgressError(f"task id {task_id!r} must use only letters, digits, '-' and '_'")
        if not title:
            raise ProgressError(f"task '{task_id}' has no title")
        if any(e["id"] == task_id for e in entries):
            raise ProgressError(f"duplicate task id '{task_id}'")
        entries.append({
            "id": task_id, "title": title, "file": f"tasks/{task_id}.md",
            "depends_on": list(task.get("depends_on") or []), "status": "new", "rejections": 0, "note": "",
        })
    data = {"feature": feature, "status": "open", "test_command": test_command.strip(), "tasks": entries}
    for entry in entries:
        for dependency in entry["depends_on"]:
            if dependency != entry["id"]:
                _task(data, dependency)
    _check_no_cycle(entries)
    _save(root, data)
    return data


def _view(feature, task):
    return {**task, "path": f"specs/{feature}/{task['file']}"}


def next_tasks(root, feature):
    """Say what to work on: `ready` lists the new tasks whose dependencies are all done."""
    data = _load(root, feature)
    result = {"feature": feature, "test_command": data["test_command"],
              "ready": [], "dev": [], "review": [], "real-testing": [], "escalated": [], "waiting": []}
    for task in data["tasks"]:
        if task["status"] == "new":
            if _unfinished_dependencies(data, task):
                result["waiting"].append(task["id"])
            else:
                result["ready"].append(_view(feature, task))
        elif _escalated(task):
            result["escalated"].append(_view(feature, task))
        elif task["status"] != "done":
            result[task["status"]].append(_view(feature, task))
    result["finished"] = all(t["status"] == "done" for t in data["tasks"])
    return result


def update(root, feature, task_id, status, note=""):
    """Move one task to its next status. Refuse any move the rules do not allow."""
    data = _load(root, feature)
    task = _task(data, task_id)
    if status not in NEXT:
        raise ProgressError(f"unknown status '{status}': use one of {', '.join(NEXT)}")
    if data["status"] == "closed":
        raise ProgressError(f"feature '{feature}' is closed")
    if status not in NEXT[task["status"]]:
        allowed = ", ".join(NEXT[task["status"]]) or "none"
        raise ProgressError(f"task '{task_id}' is '{task['status']}', it cannot become '{status}' (allowed: {allowed})")
    if task["status"] == "new":
        blockers = _unfinished_dependencies(data, task)
        if blockers:
            raise ProgressError(f"task '{task_id}' depends on tasks that are not done: {', '.join(blockers)}")
        _start_branch(root, feature)
    elif status in PROOF:
        word, field = PROOF[status]
        if not note.strip().startswith(word):
            raise ProgressError(f"task '{task_id}' stays in {task['status']}: '{status}' needs the output of "
                                f"the {task['status']} agent as note, and its first line is {word}")
        if status == "done":
            code, output = run_tests(data["test_command"], Path(root))
            if code != 0:
                raise ProgressError(f"task '{task_id}' stays in {task['status']}: the test command failed "
                                    f"(exit {code}): {data['test_command']}\n{output[-2000:]}")
        task[field] = note.strip()
    elif status == "dev":
        if not note.strip():
            raise ProgressError("a task sent back to dev needs a note with the remarks")
        task["rejections"] += 1
        task["note"] = note.strip()
    task["status"] = status
    result = {**_view(feature, task), "escalate": _escalated(task)}
    if status == "done":
        result["commit"] = _record(root, data, f"{feature} {task_id}: {task['title']}")
    else:
        _save(root, data)
    return result


def status(root, feature=None):
    """Summarize one feature, or every feature when no name is given."""
    if feature is None:
        folders = sorted(p.parent.name for p in (Path(root) / "specs").glob("*/progress.json"))
        return [status(root, name) for name in folders]
    data = _load(root, feature)
    counts = {name: sum(t["status"] == name for t in data["tasks"]) for name in NEXT}
    remaining = [t["id"] for t in data["tasks"] if t["status"] != "done"]
    return {"feature": feature, "status": data["status"], "counts": counts,
            "tasks": {t["id"]: t["status"] for t in data["tasks"]},
            "rejections": {t["id"]: t["rejections"] for t in data["tasks"]},
            "remaining": remaining, "finished": not remaining}


def dashboard(root, feature=None):
    """Give the text to show to a human: one block per feature, one line per task."""
    blocks = []
    for name in [feature] if feature else [summary["feature"] for summary in status(root)]:
        data = _load(root, name)
        rows = [("TASK", "STATUS", "REJECTIONS", "TITLE")] + [
            (t["id"], t["status"] + ", escalated" * _escalated(t), str(t["rejections"]), t["title"])
            for t in data["tasks"]]
        widths = [max(len(row[column]) for row in rows) for column in range(3)] + [0]
        done = sum(t["status"] == "done" for t in data["tasks"])
        lines = [f"{name} ({data['status']}): {done} of {len(data['tasks'])} tasks done"]
        lines += ["  " + "  ".join(cell.ljust(width) for cell, width in zip(row, widths)) for row in rows]
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) or "No feature: specs/ holds no progress.json."


def _close(root, data):
    """Close an open feature when every task is done and the test command passes. Return the problems."""
    feature = data["feature"]
    if data["status"] != "open":
        return []
    ask = f" (rejected {MAX_REJECTIONS} times: ask the human partner what to do)"
    problems = [f"{feature}: task {t['id']} is '{t['status']}', not 'done'" + ask * _escalated(t)
                for t in data["tasks"] if t["status"] != "done"]
    if problems:
        return problems
    code, output = run_tests(data["test_command"], Path(root))
    if code != 0:
        return [f"{feature}: test command failed: {data['test_command']}",
                *(f"  {line}" for line in output.splitlines()[-10:])]
    data["status"] = "closed"
    try:
        _record(root, data, f"{feature}: closed", f"specs/{feature}/progress.json")
    except ProgressError as error:
        return [f"{feature}: {error}"]
    return []


def verify(root):
    """Check every open, started feature. Return the problems, or [] when there is none.

    A feature with all tasks done and a passing test command becomes closed.
    """
    problems = []
    for summary in status(root):
        data = _load(root, summary["feature"])
        if any(t["status"] != "new" for t in data["tasks"]):
            problems += [f"FAIL: {line}" for line in _close(root, data)]
    return problems


def open_pull_request(root, branch, title, body):
    """Open the pull request of a pushed branch with the GitHub command line. Return (exit code, output)."""
    return _run(["gh", "pr", "create", "--head", branch, "--title", title, "--body", body], root)


def pull_request(root, feature):
    """Close a finished feature, push its branch and open its pull request."""
    data = _load(root, feature)
    problems = _close(root, data)
    if problems:
        raise ProgressError("\n".join(problems))
    branch = _branch(root)
    if not branch:
        raise ProgressError("no pull request: the project is not on a branch of a git repository")
    code, output = _git(root, "ls-remote", "--symref", "origin", "HEAD")
    if code != 0:
        raise ProgressError(f"no pull request: the remote 'origin' does not answer: {output}")
    if output.startswith(f"ref: refs/heads/{branch}\t"):
        raise ProgressError(f"no pull request: the feature is on the default branch '{branch}'")
    code, output = _git(root, "push", "--set-upstream", "origin", branch)
    if code != 0:
        raise ProgressError(f"no pull request: the push of the branch '{branch}' failed: {output}")
    tasks = "\n".join(f"- {t['id']}: {t['title']}" for t in data["tasks"])
    body = (f"Feature `{feature}`, developed with the tdd-loop workflow. Spec: `specs/{feature}/spec.md`.\n\n"
            f"{tasks}\n\nTest command: `{data['test_command']}`")
    code, output = open_pull_request(root, branch, feature, body)
    if code != 0:
        raise ProgressError(f"the branch '{branch}' is pushed, but the pull request is not open: {output}")
    return {"feature": feature, "branch": branch, "url": (output.splitlines() or [""])[-1]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="project root (default: current folder)")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("create", help="create progress.json from a JSON task list")
    add.add_argument("feature")
    add.add_argument("--test-command", required=True)
    add.add_argument("--tasks", default="-", help="JSON file with the task list (default: standard input)")
    move = commands.add_parser("update", help="move one task to its next status")
    move.add_argument("feature")
    move.add_argument("task")
    move.add_argument("status", choices=list(NEXT))
    move.add_argument("--note", default="")
    commands.add_parser("next", help="list the tasks to work on").add_argument("feature")
    show = commands.add_parser("status", help="show the dashboard of one or every feature: its tasks and their status")
    show.add_argument("feature", nargs="?")
    show.add_argument("--json", action="store_true", help="print the summary as JSON instead of the dashboard")
    commands.add_parser("verify", help="exit 1 while a started feature has unfinished tasks or failing tests")
    commands.add_parser("pr", help="close a finished feature, push its branch and open its pull request"
                        ).add_argument("feature")
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            problems = verify(args.root)
            print("\n".join(problems) if problems else "{}")
            return 1 if problems else 0
        if args.command == "create":
            text = sys.stdin.read() if args.tasks == "-" else Path(args.tasks).read_text()
            result = create(args.root, args.feature, args.test_command, json.loads(text))
        elif args.command == "update":
            result = update(args.root, args.feature, args.task, args.status, args.note)
        elif args.command == "next":
            result = next_tasks(args.root, args.feature)
        elif args.command == "pr":
            result = pull_request(args.root, args.feature)
        elif args.json:
            result = status(args.root, args.feature)
        else:
            print(dashboard(args.root, args.feature))
            return 0
    except (ProgressError, ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
