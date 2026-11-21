import asyncio
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mcp import Client, StdioServerParameters

import server

TASKS = [{"id": "T1", "title": "Reject an empty password"},
         {"id": "T2", "title": "Lock after 3 failures", "depends_on": ["T1"]}]
CREATE = {"feature": "login", "test_command": "exit 0", "tasks": TASKS}


async def session(target, calls):
    """Open one client session, run the tool calls in order, return (tool names, results)."""
    async with Client(target) as client:
        names = sorted(tool.name for tool in (await client.list_tools()).tools)
        return names, [await client.call_tool(name, arguments) for name, arguments in calls]


def text(result):
    return result.content[0].text


class ServerTest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        environment = patch.dict(os.environ, {"TDD_PROGRESS_ROOT": folder.name})
        environment.start()
        self.addCleanup(environment.stop)

    def call(self, *calls):
        return asyncio.run(session(server.server, calls))

    def test_exposes_the_four_tools(self):
        names, _ = self.call()
        self.assertEqual(names, ["progress_create", "progress_next", "progress_status", "progress_update"])

    def test_runs_a_task_from_new_to_done(self):
        _, results = self.call(
            ("progress_create", CREATE),
            ("progress_next", {"feature": "login"}),
            ("progress_update", {"feature": "login", "task_id": "T1", "status": "dev"}),
            ("progress_update", {"feature": "login", "task_id": "T1", "status": "review"}),
            ("progress_update", {"feature": "login", "task_id": "T1", "status": "real-testing",
                                 "note": "APPROVED\n- test_rejects_empty_password"}),
            ("progress_update", {"feature": "login", "task_id": "T1", "status": "done",
                                 "note": "PASSED\n- B1: ran the program with an empty password -> it refused"}),
            ("progress_status", {"feature": "login"}),
            ("progress_status", {}),
        )
        self.assertFalse(any(result.is_error for result in results))
        self.assertEqual([task["id"] for task in json.loads(text(results[1]))["ready"]], ["T1"])
        self.assertEqual(json.loads(text(results[6]))["remaining"], ["T2"])
        self.assertEqual(json.loads(text(results[7]))["features"][0]["feature"], "login")
        for result in results[6:8]:
            self.assertEqual(json.loads(text(result))["dashboard"].splitlines(), [
                "login (open): 1 of 2 tasks done",
                "  TASK  STATUS  REJECTIONS  TITLE",
                "  T1    done    0           Reject an empty password",
                "  T2    new     0           Lock after 3 failures",
            ])
        stored = json.loads((self.root / "specs" / "login" / "progress.json").read_text())
        self.assertEqual([task["status"] for task in stored["tasks"]], ["done", "new"])

    def test_refused_move_returns_the_reason(self):
        _, results = self.call(
            ("progress_create", CREATE),
            ("progress_update", {"feature": "login", "task_id": "T1", "status": "review"}),
            ("progress_update", {"feature": "login", "task_id": "T2", "status": "dev"}),
        )
        self.assertEqual([result.is_error for result in results], [False, True, True])
        self.assertIn("allowed: dev", text(results[1]))
        self.assertIn("not done: T1", text(results[2]))

    def test_works_as_a_real_process_over_stdio(self):
        script = str(Path(server.__file__).resolve())
        process = StdioServerParameters(command=sys.executable, args=[script], cwd=str(self.root),
                                        env={k: v for k, v in os.environ.items() if k != "TDD_PROGRESS_ROOT"})
        names, results = asyncio.run(session(process, [("progress_create", CREATE)]))
        self.assertEqual(len(names), 4)
        self.assertFalse(results[0].is_error)
        self.assertTrue((self.root / "specs" / "login" / "progress.json").exists())


if __name__ == "__main__":
    unittest.main()
