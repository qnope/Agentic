import io
import unittest
from unittest.mock import patch

import tdd_gate

UNFINISHED = ["FAIL: login: task T1 is 'real-testing', not 'done'"]
# What Claude Code gives a Stop hook in `background_tasks`: the work in flight that wakes the session at its end.
AGENT = '{"id": "a7b7bd377cc9a114b", "type": "subagent", "status": "running", "agent_type": "tdd-real-tester"}'
SHELL = '{"id": "bmn5s7qrh", "type": "shell", "status": "running", "command": "npm run dev"}'


def run(stdin, failed):
    out, err = io.StringIO(), io.StringIO()
    with patch.object(tdd_gate, "failures", return_value=failed):
        code = tdd_gate.main(io.StringIO(stdin), out, err)
    return code, out.getvalue().strip(), err.getvalue()


class HookTest(unittest.TestCase):
    def test_allows_and_prints_empty_json_when_every_feature_is_finished(self):
        self.assertEqual(run("{}", []), (0, "{}", ""))

    def test_blocks_and_names_the_unfinished_task(self):
        code, _, err = run("{}", ["FAIL: login: task T2 is 'review', not 'done'"])
        self.assertEqual(code, 2)
        self.assertIn("task T2 is 'review'", err)

    def test_blocks_and_names_the_failed_test_command(self):
        code, _, err = run("{}", ["FAIL: login: test command failed: ctest --test-dir build"])
        self.assertEqual(code, 2)
        self.assertIn("ctest --test-dir build", err)

    def test_allows_when_already_blocked_once(self):
        self.assertEqual(run('{"stop_hook_active": true}', ["FAIL: login: task T2 is 'dev', not 'done'"])[0], 0)

    def test_allows_without_the_check_while_an_agent_works_in_the_background(self):
        stdin = io.StringIO('{"stop_hook_active": false, "background_tasks": [%s, %s]}' % (SHELL, AGENT))
        out = io.StringIO()
        with patch.object(tdd_gate, "failures", side_effect=AssertionError("the check ran")):
            self.assertEqual(tdd_gate.main(stdin, out, io.StringIO()), 0)
        self.assertEqual(out.getvalue().strip(), "{}")

    def test_blocks_when_no_agent_works_in_the_background(self):
        for tasks in ("[]", "[%s]" % SHELL, '"subagent"', "7"):
            with self.subTest(background_tasks=tasks):
                self.assertEqual(run('{"background_tasks": %s}' % tasks, UNFINISHED)[0], 2)

    def test_allows_on_invalid_input(self):
        self.assertEqual(run("not json", [])[0], 0)

    def test_runs_the_verify_command_of_the_progress_tool(self):
        self.assertEqual(tdd_gate.COMMAND, ["python3", "mcp-servers/tdd-progress/progress.py", "verify"])
