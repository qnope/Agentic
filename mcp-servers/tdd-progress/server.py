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
    "A task goes new -> dev -> review -> done; a review can send it back to dev. "
    "Never edit progress.json by hand: use these tools."
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

    ready: new tasks whose dependencies are all done. dev, review: tasks in progress.
    escalated: tasks rejected 3 times, the human partner decides. waiting: ids of new
    tasks with an unfinished dependency. finished: true when every task is done.
    test_command: the command that runs all the tests.
    """
    return call(progress.next_tasks, feature)


@server.tool()
def progress_update(feature: str, task_id: str, status: Literal["dev", "review", "done"], note: str = "") -> dict:
    """Move one task to its next status. Any other move is refused, with the reason.

    new -> dev: needs every dependency done. dev -> review. review -> done: note is
    required and holds the reviewer output, whose first line is APPROVED; the tool then
    runs the test command, refused while it fails. review -> dev: the review rejected
    the task, note is required and holds the review remarks. The result has
    escalate: true when the task was rejected 3 times: stop and ask the human partner.
    """
    return call(progress.update, feature, task_id, status, note)


@server.tool()
def progress_status(feature: str = "") -> dict:
    """Count the tasks per status and list the remaining ones.

    With a feature name: that feature. With no name: every feature, under the key features.
    """
    return call(progress.status, feature) if feature else {"features": call(progress.status)}


if __name__ == "__main__":
    server.run()
