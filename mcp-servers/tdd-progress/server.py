#!/usr/bin/env python3
"""MCP server `tdd-progress`: gives the tdd-loop workflow the operations of progress.py.

Start it from the project root: `python3 mcp-servers/tdd-progress/server.py` (stdio).
The project root is the current folder, or the `TDD_PROGRESS_ROOT` environment variable.
Needs the official SDK: `pip install "mcp>=2"`.
"""
import os
from typing import Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel

import progress

server = MCPServer("tdd-progress", log_level="WARNING", instructions=(
    "Tracks the tasks of a feature in specs/<feature>/progress.json. "
    "A task goes new -> dev -> review -> real-testing -> done; "
    "a review or a real test can send it back to dev. "
    "Never edit progress.json by hand: use these tools. "
    "In a git repository, the tools commit each done task and open the pull request of a finished feature."
))


class Task(BaseModel):
    id: str
    title: str
    depends_on: list[str] = []


def call(operation, *arguments):
    """Run one progress.py operation. A refusal reaches the caller with its reason."""
    try:
        return operation(os.environ.get("TDD_PROGRESS_ROOT", "."), *arguments)
    except progress.ProgressError as error:
        raise ToolError(str(error)) from error


@server.tool()
def progress_create(feature: str, test_command: str, tasks: list[Task]) -> dict:
    """Create specs/<feature>/progress.json with every task in status new.

    feature: kebab-case name. test_command: one shell command, run from the project
    root, that builds and runs all the tests and exits 0 only when they pass.
    tasks: each has an id (T1, T2, ...), a title and depends_on (ids of the tasks that
    must be done first). Refused: duplicate id, unknown dependency, dependency cycle,
    a feature that has already started.
    """
    return call(progress.create, feature, test_command, [task.model_dump() for task in tasks])


@server.tool()
def progress_next(feature: str) -> dict:
    """List what to work on in a feature.

    ready: new tasks whose dependencies are all done. dev, review, real-testing: tasks in progress.
    escalated: tasks rejected 3 times, the human partner decides. waiting: ids of new
    tasks with an unfinished dependency. finished: true when every task is done.
    test_command: the command that runs all the tests.
    """
    return call(progress.next_tasks, feature)


@server.tool()
def progress_update(feature: str, task_id: str, status: Literal["dev", "review", "real-testing", "done"],
                    note: str = "") -> dict:
    """Move one task to its next status. Any other move is refused, with the reason.

    new -> dev: needs every dependency done; in a git repository on the default branch,
    the tool first creates the branch feature/<feature>. dev -> review. review ->
    real-testing: note is required and holds the reviewer output, whose first line is APPROVED.
    real-testing -> done: note is required and holds the real tester output, whose first
    line is PASSED; the tool then runs the test command, refused while it fails; then it
    commits every change of the project with the message "<feature> <task id>: <title>",
    refused while the commit fails. The result has commit: its short hash, or "" when the
    project is not in git.
    review -> dev or real-testing -> dev: the task is rejected, note is required and
    holds the remarks. The result has escalate: true when the task was rejected 3 times:
    stop and ask the human partner.
    """
    return call(progress.update, feature, task_id, status, note)


@server.tool()
def progress_pull_request(feature: str) -> dict:
    """Close a finished feature, push its branch and open its pull request.

    The result has branch and url. Refused, with the reason, when: a task is not done,
    the test command fails, the project is not on a branch of a git repository, the
    branch is the default branch of the remote origin, the push fails, or the GitHub
    command line `gh` cannot open the pull request.
    """
    return call(progress.pull_request, feature)


@server.tool()
def progress_status(feature: str = "") -> dict:
    """Show the progress: the tasks of each feature, with their status and their number of rejections.

    With a feature name: that feature. With no name: every feature, under the key features.
    A feature has counts (tasks per status), tasks (status of each task), rejections (times
    each task was sent back to dev), remaining and finished. dashboard: the same as text.
    When the human partner asks for the progress, show dashboard as it is.
    """
    summary = call(progress.status, feature) if feature else {"features": call(progress.status)}
    return {**summary, "dashboard": call(progress.dashboard, feature or None)}


if __name__ == "__main__":
    server.run()
