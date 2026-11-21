import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import progress

TASKS = [
    {"id": "T1", "title": "Reject an empty password"},
    {"id": "T2", "title": "Hash the password"},
    {"id": "T3", "title": "Lock after 3 failures", "depends_on": ["T1", "T2"]},
]
PASS, FAIL = (0, "all green"), (1, "test_lock ... FAILED")
REVIEW = "APPROVED\n- test_rejects_empty_password"


class Base(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)

    def create(self, feature="login", tasks=TASKS, command="run-tests"):
        return progress.create(self.root, feature, command, tasks)

    def move(self, task_id, *statuses, feature="login", note=REVIEW, tests=PASS):
        with patch.object(progress, "run_tests", return_value=tests) as run:
            for status in statuses:
                result = progress.update(self.root, feature, task_id, status, note)
        return result, run

    def stored(self, feature="login"):
        return json.loads((self.root / "specs" / feature / "progress.json").read_text())

    def refused(self, text, call, *args, **kwargs):
        with self.assertRaises(progress.ProgressError) as caught:
            call(*args, **kwargs)
        self.assertIn(text, str(caught.exception))


class CreateTest(Base):
    def test_writes_open_feature_with_new_tasks(self):
        self.create()
        data = self.stored()
        self.assertEqual((data["feature"], data["status"], data["test_command"]), ("login", "open", "run-tests"))
        self.assertEqual(data["tasks"][0], {
            "id": "T1", "title": "Reject an empty password", "file": "tasks/T1.md",
            "depends_on": [], "status": "new", "rejections": 0, "note": "",
        })
        self.assertEqual(data["tasks"][2]["depends_on"], ["T1", "T2"])

    def test_refuses_bad_feature_name(self):
        for name in ("../login", "My Feature", ""):
            self.refused("kebab-case", self.create, feature=name)

    def test_refuses_bad_task_lists(self):
        self.refused("at least one task", self.create, tasks=[])
        self.refused("duplicate", self.create, tasks=[TASKS[0], TASKS[0]])
        self.refused("title", self.create, tasks=[{"id": "T1"}])
        self.refused("unknown task 'T9'", self.create, tasks=[{"id": "T1", "title": "a", "depends_on": ["T9"]}])
        self.refused("test command", self.create, command=" ")

    def test_refuses_dependency_cycle(self):
        cycle = [
            {"id": "T1", "title": "a", "depends_on": ["T2"]},
            {"id": "T2", "title": "b", "depends_on": ["T1"]},
        ]
        self.refused("cycle", self.create, tasks=cycle)
        self.refused("cycle", self.create, tasks=[{"id": "T1", "title": "a", "depends_on": ["T1"]}])

    def test_overwrites_only_a_feature_that_has_not_started(self):
        self.create()
        self.create(tasks=TASKS[:1])
        self.assertEqual(len(self.stored()["tasks"]), 1)
        self.move("T1", "dev")
        self.refused("already started", self.create)


class NextTest(Base):
    def test_ready_tasks_have_all_dependencies_done(self):
        self.create()
        result = progress.next_tasks(self.root, "login")
        self.assertEqual([t["id"] for t in result["ready"]], ["T1", "T2"])
        self.assertEqual(result["ready"][0]["path"], "specs/login/tasks/T1.md")
        self.assertEqual((result["waiting"], result["finished"]), (["T3"], False))
        self.assertEqual(result["test_command"], "run-tests")

    def test_dependent_task_becomes_ready_and_feature_finishes(self):
        self.create()
        self.move("T1", "dev", "review", "done")
        self.move("T2", "dev", "review")
        result = progress.next_tasks(self.root, "login")
        self.assertEqual((result["ready"], [t["id"] for t in result["review"]]), ([], ["T2"]))
        self.move("T2", "done")
        self.assertEqual([t["id"] for t in progress.next_tasks(self.root, "login")["ready"]], ["T3"])
        self.move("T3", "dev", "review", "done")
        self.assertTrue(progress.next_tasks(self.root, "login")["finished"])


class UpdateTest(Base):
    def test_follows_new_dev_review_done(self):
        self.create()
        result, run = self.move("T1", "dev", "review", "done")
        self.assertEqual(result["status"], "done")
        self.assertEqual(self.stored()["tasks"][0]["status"], "done")
        run.assert_called_once_with("run-tests", self.root)

    def test_refuses_skipped_or_backward_status(self):
        self.create()
        self.refused("allowed: dev", self.move, "T1", "review")
        self.refused("allowed: dev", self.move, "T1", "done")
        self.move("T1", "dev", "review", "done")
        self.refused("allowed: none", self.move, "T1", "dev")

    def test_refuses_dev_while_a_dependency_is_not_done(self):
        self.create()
        self.move("T1", "dev", "review", "done")
        self.refused("T2", self.move, "T3", "dev")
        self.assertEqual(self.stored()["tasks"][2]["status"], "new")

    def test_done_needs_the_reviewer_output_and_keeps_it(self):
        self.create()
        self.move("T1", "dev", "review")
        self.refused("APPROVED", self.move, "T1", "done", note="")
        self.refused("APPROVED", self.move, "T1", "done", note="Looks fine.")
        self.assertEqual(self.stored()["tasks"][0]["status"], "review")
        self.move("T1", "done")
        self.assertEqual(self.stored()["tasks"][0]["note"], REVIEW)

    def test_refuses_done_while_the_tests_fail(self):
        self.create()
        self.move("T1", "dev", "review")
        self.refused("test_lock ... FAILED", self.move, "T1", "done", tests=FAIL)
        self.assertEqual(self.stored()["tasks"][0]["status"], "review")

    def test_rejection_needs_a_note_and_escalates_at_the_third(self):
        self.create()
        self.move("T1", "dev", "review")
        self.refused("note", self.move, "T1", "dev", note=" ")
        result, run = self.move("T1", "dev", note="No test for the empty string.")
        self.assertEqual((result["rejections"], result["escalate"]), (1, False))
        self.assertEqual(self.stored()["tasks"][0]["note"], "No test for the empty string.")
        run.assert_not_called()
        self.move("T1", "review", "dev", note="Still missing.")
        result, _ = self.move("T1", "review", "dev", note="Still missing.")
        self.assertEqual((result["rejections"], result["escalate"]), (3, True))
        self.assertEqual([t["id"] for t in progress.next_tasks(self.root, "login")["escalated"]], ["T1"])

    def test_refuses_unknown_feature_task_and_status(self):
        self.refused("no progress file", self.move, "T1", "dev")
        self.create()
        self.refused("unknown task 'T9'", self.move, "T9", "dev")
        self.refused("unknown status", self.move, "T1", "started")


class StatusTest(Base):
    def test_counts_and_remaining(self):
        self.create()
        self.move("T1", "dev", "review", "done")
        self.move("T2", "dev")
        result = progress.status(self.root, "login")
        self.assertEqual(result["counts"], {"new": 1, "dev": 1, "review": 0, "done": 1})
        self.assertEqual((result["remaining"], result["finished"], result["status"]), (["T2", "T3"], False, "open"))
        self.assertEqual(result["tasks"], {"T1": "done", "T2": "dev", "T3": "new"})

    def test_lists_every_feature(self):
        self.create()
        self.create(feature="signup", tasks=TASKS[:1])
        self.assertEqual([s["feature"] for s in progress.status(self.root)], ["login", "signup"])


class VerifyTest(Base):
    def verify(self, tests=PASS):
        with patch.object(progress, "run_tests", return_value=tests) as run:
            return progress.verify(self.root), run

    def test_ignores_missing_and_not_started_features(self):
        self.assertEqual(self.verify()[0], [])
        self.create()
        lines, run = self.verify()
        self.assertEqual(lines, [])
        run.assert_not_called()

    def test_names_unfinished_tasks_without_running_the_tests(self):
        self.create()
        self.move("T1", "dev")
        lines, run = self.verify()
        self.assertEqual(lines[0], "FAIL: login: task T1 is 'dev', not 'done'")
        self.assertEqual(len(lines), 3)
        run.assert_not_called()

    def test_says_to_ask_the_human_for_a_task_rejected_3_times(self):
        self.create()
        self.move("T1", "dev", "review", "dev", "review", "dev", "review", "dev", note="Wrong.")
        self.assertEqual(self.verify()[0][0], "FAIL: login: task T1 is 'dev', not 'done' "
                         "(rejected 3 times: ask the human partner what to do)")

    def test_closes_the_feature_when_all_done_and_tests_pass(self):
        self.create(tasks=TASKS[:1])
        self.move("T1", "dev", "review", "done")
        self.assertEqual(self.verify()[0], [])
        self.assertEqual(self.stored()["status"], "closed")
        self.verify()[1].assert_not_called()
        self.refused("closed", self.create, tasks=TASKS[:1])

    def test_reports_failing_tests_and_keeps_the_feature_open(self):
        self.create(tasks=TASKS[:1])
        self.move("T1", "dev", "review", "done")
        lines, _ = self.verify(tests=FAIL)
        self.assertEqual(lines[0], "FAIL: login: test command failed: run-tests")
        self.assertIn("test_lock ... FAILED", lines[1])
        self.assertEqual(self.stored()["status"], "open")


class CommandLineTest(Base):
    def run_cli(self, *args, stdin=""):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), patch("sys.stdin", io.StringIO(stdin)):
            code = progress.main(["--root", str(self.root), *args])
        return code, out.getvalue(), err.getvalue()

    def test_create_update_next_status(self):
        code, out, _ = self.run_cli("create", "login", "--test-command", "true", stdin=json.dumps(TASKS))
        self.assertEqual((code, json.loads(out)["status"]), (0, "open"))
        code, out, _ = self.run_cli("update", "login", "T1", "dev")
        self.assertEqual((code, json.loads(out)["status"]), (0, "dev"))
        code, out, _ = self.run_cli("next", "login")
        self.assertEqual([t["id"] for t in json.loads(out)["ready"]], ["T2"])
        code, out, _ = self.run_cli("status", "login")
        self.assertEqual(json.loads(out)["remaining"], ["T1", "T2", "T3"])

    def test_error_goes_to_stderr_with_exit_code_1(self):
        code, out, err = self.run_cli("update", "login", "T1", "dev")
        self.assertEqual((code, out), (1, ""))
        self.assertTrue(err.startswith("ERROR: "))

    def test_verify_runs_the_real_test_command(self):
        self.run_cli("create", "login", "--test-command", "echo boom && exit 3", stdin=json.dumps(TASKS[:1]))
        self.run_cli("update", "login", "T1", "dev")
        self.run_cli("update", "login", "T1", "review")
        code, _, err = self.run_cli("update", "login", "T1", "done", "--note", REVIEW)
        self.assertEqual(code, 1)
        self.assertIn("boom", err)
        code, out, _ = self.run_cli("verify")
        self.assertEqual(code, 1)
        self.assertIn("FAIL: login: task T1 is 'review', not 'done'", out)


if __name__ == "__main__":
    unittest.main()
