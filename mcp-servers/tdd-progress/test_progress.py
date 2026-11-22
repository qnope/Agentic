import contextlib
import io
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
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
REAL_TEST = "PASSED\n- B1: ran the program with an empty password -> it printed 'password required'"
NOTES = {"real-testing": REVIEW, "done": REAL_TEST}
ALONE = [TASKS[0], {**TASKS[1], "depends_on": ["T1"]}]  # One task at a time: each one is worked in the project root.


class Base(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)

    def create(self, feature="login", tasks=TASKS, command="run-tests"):
        return progress.create(self.root, feature, command, tasks)

    def move(self, task_id, *statuses, feature="login", note=None, tests=PASS):
        """Move a task through the statuses. Without a note, each status gets the output it needs."""
        with patch.object(progress, "run_tests", return_value=tests) as run:
            for status in statuses:
                text = NOTES.get(status, "") if note is None else note
                result = progress.update(self.root, feature, task_id, status, text)
        return result, run

    def finish(self, task_id, **options):
        return self.move(task_id, "dev", "review", "real-testing", "done", **options)

    def stored(self, feature="login"):
        return json.loads((self.root / "specs" / feature / "progress.json").read_text())

    def refused(self, text, call, *args, **kwargs):
        with self.assertRaises(progress.ProgressError) as caught:
            call(*args, **kwargs)
        self.assertIn(text, str(caught.exception))


def git(folder, *arguments):
    return subprocess.run(["git", *arguments], cwd=folder, capture_output=True, text=True, check=True).stdout.strip()


class GitBase(Base):
    """The project root is a git repository on the branch main, with one commit and the remote origin."""

    def setUp(self):
        super().setUp()
        own_config = patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"})
        own_config.start()
        self.addCleanup(own_config.stop)
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.remote = Path(folder.name)
        for place, option in ((self.root, "--quiet"), (self.remote, "--bare")):
            git(place, "init", "--quiet", option)
            git(place, "symbolic-ref", "HEAD", "refs/heads/main")
        git(self.root, "config", "user.name", "Test")
        git(self.root, "config", "user.email", "test@example.com")
        (self.root / "README.md").write_text("project\n")
        git(self.root, "add", "--all")
        git(self.root, "commit", "--quiet", "--message", "initial")
        git(self.root, "remote", "add", "origin", str(self.remote))
        git(self.root, "push", "--quiet", "origin", "main")

    def subjects(self, branch="HEAD", place=None):
        return git(place or self.root, "log", "--format=%s", branch).splitlines()

    def refuse_every_commit(self):
        hook = self.root / ".git" / "hooks" / "pre-commit"
        hook.parent.mkdir(exist_ok=True)
        hook.write_text("#!/bin/sh\necho 'lint failed'\nexit 1\n")
        hook.chmod(0o755)


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
        self.finish("T1")
        self.move("T2", "dev", "review")
        result = progress.next_tasks(self.root, "login")
        self.assertEqual((result["ready"], [t["id"] for t in result["review"]]), ([], ["T2"]))
        self.move("T2", "real-testing")
        result = progress.next_tasks(self.root, "login")
        self.assertEqual((result["review"], [t["id"] for t in result["real-testing"]]), ([], ["T2"]))
        self.move("T2", "done")
        self.assertEqual([t["id"] for t in progress.next_tasks(self.root, "login")["ready"]], ["T3"])
        self.finish("T3")
        self.assertTrue(progress.next_tasks(self.root, "login")["finished"])


class UpdateTest(Base):
    def test_follows_new_dev_review_real_testing_done(self):
        self.create()
        result, run = self.finish("T1")
        self.assertEqual(result["status"], "done")
        self.assertEqual(self.stored()["tasks"][0]["status"], "done")
        run.assert_called_once_with("run-tests", self.root)

    def test_refuses_skipped_or_backward_status(self):
        self.create()
        self.refused("allowed: dev", self.move, "T1", "review")
        self.refused("allowed: dev", self.move, "T1", "done")
        self.move("T1", "dev", "review")
        self.refused("allowed: real-testing, dev", self.move, "T1", "done")
        self.move("T1", "real-testing", "done")
        self.refused("allowed: none", self.move, "T1", "dev")

    def test_refuses_dev_while_a_dependency_is_not_done(self):
        self.create()
        self.finish("T1")
        self.refused("T2", self.move, "T3", "dev")
        self.assertEqual(self.stored()["tasks"][2]["status"], "new")

    def test_real_testing_needs_the_reviewer_output_and_keeps_it(self):
        self.create()
        self.move("T1", "dev", "review")
        self.refused("APPROVED", self.move, "T1", "real-testing", note="")
        self.refused("APPROVED", self.move, "T1", "real-testing", note="Looks fine.")
        self.assertEqual(self.stored()["tasks"][0]["status"], "review")
        _, run = self.move("T1", "real-testing")
        self.assertEqual(self.stored()["tasks"][0]["review"], REVIEW)
        run.assert_not_called()

    def test_done_needs_the_real_tester_output_and_keeps_it(self):
        self.create()
        self.move("T1", "dev", "review", "real-testing")
        self.refused("PASSED", self.move, "T1", "done", note="")
        self.refused("PASSED", self.move, "T1", "done", note=REVIEW)
        self.assertEqual(self.stored()["tasks"][0]["status"], "real-testing")
        self.move("T1", "done")
        task = self.stored()["tasks"][0]
        self.assertEqual((task["review"], task["real_testing"], task["note"]), (REVIEW, REAL_TEST, ""))

    def test_refuses_done_while_the_tests_fail(self):
        self.create()
        self.move("T1", "dev", "review", "real-testing")
        self.refused("test_lock ... FAILED", self.move, "T1", "done", tests=FAIL)
        self.assertEqual(self.stored()["tasks"][0]["status"], "real-testing")

    def test_rejection_needs_a_note_and_escalates_at_the_third(self):
        self.create()
        self.move("T1", "dev", "review")
        self.refused("note", self.move, "T1", "dev", note=" ")
        result, run = self.move("T1", "dev", note="No test for the empty string.")
        self.assertEqual((result["rejections"], result["escalate"]), (1, False))
        self.assertEqual(self.stored()["tasks"][0]["note"], "No test for the empty string.")
        run.assert_not_called()
        self.move("T1", "review", "real-testing")
        self.refused("note", self.move, "T1", "dev", note="")
        result, _ = self.move("T1", "dev", note="The program prints nothing.")
        self.assertEqual((result["rejections"], result["note"]), (2, "The program prints nothing."))
        result, _ = self.move("T1", "review", "dev", note="Still missing.")
        self.assertEqual((result["rejections"], result["escalate"]), (3, True))
        self.assertEqual([t["id"] for t in progress.next_tasks(self.root, "login")["escalated"]], ["T1"])

    def test_refuses_unknown_feature_task_and_status(self):
        self.refused("no progress file", self.move, "T1", "dev")
        self.create()
        self.refused("unknown task 'T9'", self.move, "T9", "dev")
        self.refused("unknown status", self.move, "T1", "started")

    @unittest.skipIf(os.name == "nt", "needs a file lock")
    def test_updates_made_at_the_same_time_are_all_recorded(self):
        self.create()
        load = progress._load

        def slow_load(*arguments):
            data = load(*arguments)
            time.sleep(0.05)
            return data

        with patch.object(progress, "_load", slow_load):
            threads = [threading.Thread(target=progress.update, args=(self.root, "login", task_id, "dev"))
                       for task_id in ("T1", "T2")]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        self.assertEqual([task["status"] for task in self.stored()["tasks"]], ["dev", "dev", "new"])


class BranchTest(GitBase):
    def branch(self):
        return git(self.root, "symbolic-ref", "--short", "HEAD")

    def test_dev_on_the_default_branch_starts_the_feature_branch(self):
        self.create()
        self.move("T1", "dev")
        self.assertEqual(self.branch(), "feature/login")
        self.move("T2", "dev")
        self.assertEqual(self.branch(), "feature/login")

    def test_dev_on_another_branch_keeps_it(self):
        git(self.root, "checkout", "--quiet", "-b", "work")
        self.create()
        self.move("T1", "dev")
        self.assertEqual(self.branch(), "work")

    def test_the_default_branch_is_the_one_origin_names(self):
        git(self.root, "checkout", "--quiet", "-b", "trunk")
        git(self.root, "update-ref", "refs/remotes/origin/trunk", "HEAD")
        git(self.root, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
        self.create()
        self.move("T1", "dev")
        self.assertEqual(self.branch(), "feature/login")
        git(self.root, "checkout", "--quiet", "main")
        self.move("T2", "dev")
        self.assertEqual(self.branch(), "main")

    def test_refuses_dev_when_the_feature_branch_cannot_be_created(self):
        git(self.root, "branch", "feature/login")
        self.create()
        self.refused("feature/login", self.move, "T1", "dev")
        self.assertEqual((self.branch(), self.stored()["tasks"][0]["status"]), ("main", "new"))


class CommitTest(GitBase):
    def test_done_commits_the_work_of_the_task_with_its_id(self):
        self.create(tasks=ALONE)
        self.move("T1", "dev")
        (self.root / "password.py").write_text("def check(): ...\n")
        result, _ = self.move("T1", "review", "real-testing", "done")
        self.assertEqual(self.subjects(), ["login T1: Reject an empty password", "initial"])
        self.assertEqual(result["commit"], git(self.root, "rev-parse", "--short", "HEAD"))
        self.assertEqual(git(self.root, "status", "--porcelain"), "")
        self.assertIn("password.py", git(self.root, "show", "--name-only", "--format=", "HEAD"))
        committed = json.loads(git(self.root, "show", "HEAD:specs/login/progress.json"))
        self.assertEqual(committed["tasks"][0]["status"], "done")

    def test_only_the_move_to_done_commits(self):
        self.create()
        result, _ = self.move("T1", "dev", "review", "real-testing")
        self.assertNotIn("commit", result)
        self.assertEqual(self.subjects(), ["initial"])

    def test_refuses_done_when_the_commit_fails(self):
        self.create(tasks=ALONE)
        self.move("T1", "dev", "review", "real-testing")
        self.refuse_every_commit()
        self.refused("lint failed", self.move, "T1", "done")
        task = self.stored()["tasks"][0]
        self.assertEqual((task["status"], "real_testing" in task), ("real-testing", False))
        self.assertEqual(self.subjects(), ["initial"])

    def test_done_with_nothing_to_commit_gives_no_commit(self):
        (self.root / ".gitignore").write_text("specs/\n")
        git(self.root, "add", "--all")
        git(self.root, "commit", "--quiet", "--message", "ignore the specs")
        self.create(tasks=ALONE)
        result, _ = self.finish("T1")
        self.assertEqual((result["status"], result["commit"]), ("done", ""))
        self.assertEqual(self.subjects()[0], "ignore the specs")

    def test_done_outside_git_gives_no_commit(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        self.root = Path(outside.name)
        self.create()
        self.assertEqual(self.finish("T1")[0]["commit"], "")

    def test_a_folder_inside_a_git_repository_is_not_committed(self):
        self.root = self.root / "sub" / "project"
        self.create()
        self.assertEqual(self.finish("T1")[0]["commit"], "")
        self.assertEqual((self.subjects(), git(self.root, "symbolic-ref", "--short", "HEAD")), (["initial"], "main"))


class WorktreeTest(GitBase):
    """T1 and T2 can start together: each one is developed in its own git worktree, then merged in the root."""

    def setUp(self):
        super().setUp()
        (self.root / "app.txt").write_text("base\n")
        git(self.root, "add", "--all")
        git(self.root, "commit", "--quiet", "--message", "base")
        self.create()

    def develop(self, task_id, name, text):
        """Start a task and write one file in its worktree. Return the worktree."""
        tree = self.root / self.move(task_id, "dev")[0]["worktree"]
        (tree / name).write_text(text)
        return tree

    def test_dev_gives_a_worktree_to_each_task_that_can_run_with_another(self):
        first, second = self.move("T1", "dev")[0], self.move("T2", "dev")[0]
        self.assertEqual((first["worktree"], second["worktree"]), (".worktrees/login/T1", ".worktrees/login/T2"))
        self.assertEqual(git(self.root / first["worktree"], "branch", "--show-current"), "tdd/login/T1")
        self.assertEqual((self.root / second["worktree"] / "app.txt").read_text(), "base\n")
        self.assertEqual(self.stored()["tasks"][0]["worktree"], ".worktrees/login/T1")
        self.assertEqual(progress.next_tasks(self.root, "login")["dev"][1]["worktree"], ".worktrees/login/T2")
        self.assertEqual(git(self.root, "status", "--porcelain", "--", ".", ":(exclude)specs"), "")

    def test_the_worktree_of_a_task_holds_the_work_of_the_tasks_it_depends_on(self):
        self.create(tasks=[TASKS[0], TASKS[1], {"id": "T3", "title": "Lock after 3 failures", "depends_on": ["T1"]}])
        self.develop("T1", "one.txt", "1\n")
        self.develop("T2", "two.txt", "2\n")
        self.refused("not done: T1", self.move, "T3", "dev")
        self.move("T1", "review", "real-testing", "done")
        tree = self.develop("T3", "three.txt", "3\n")
        self.assertEqual(((tree / "one.txt").read_text(), (tree / "two.txt").exists()), ("1\n", False))

    def test_the_worktree_of_a_task_holds_the_work_of_a_dependency_developed_in_the_root(self):
        self.create(tasks=[TASKS[0], {**TASKS[1], "depends_on": ["T1"]}, {**TASKS[2], "depends_on": ["T1"]}])
        self.assertNotIn("worktree", self.move("T1", "dev")[0])
        (self.root / "one.txt").write_text("1\n")
        self.move("T1", "review", "real-testing", "done")
        trees = [self.develop("T2", "two.txt", "2\n"), self.develop("T3", "three.txt", "3\n")]
        self.assertEqual([(tree / "one.txt").read_text() for tree in trees], ["1\n", "1\n"])

    def test_dev_keeps_a_task_that_runs_alone_in_the_root(self):
        self.create(tasks=[TASKS[0], {"id": "T2", "title": "Hash the password", "depends_on": ["T1"]}])
        result, _ = self.move("T1", "dev")
        self.assertEqual({"worktree", "no_worktree"} & result.keys(), set())
        self.assertFalse((self.root / ".worktrees").exists())

    def test_dev_says_why_a_task_gets_no_worktree(self):
        (self.root / "notes.txt").write_text("not committed\n")
        result, _ = self.move("T1", "dev")
        self.assertIn("uncommitted changes outside specs/: notes.txt", result["no_worktree"])
        self.assertEqual((result["status"], "worktree" in result), ("dev", False))
        shutil.rmtree(self.root / ".git")
        git(self.root, "init", "--quiet")
        self.create(feature="signup")
        self.assertIn("no commit", self.move("T1", "dev", feature="signup")[0]["no_worktree"])
        shutil.rmtree(self.root / ".git")
        self.assertIn("not the top folder of a git repository",
                      self.move("T2", "dev", feature="signup")[0]["no_worktree"])

    def test_done_merges_the_worktree_in_the_one_commit_of_the_task(self):
        first, second = self.develop("T1", "one.txt", "1\n"), self.develop("T2", "two.txt", "2\n")
        result, run = self.move("T1", "review", "real-testing", "done")
        self.assertEqual([call.args[1] for call in run.call_args_list], [first, self.root])
        self.assertEqual((result["status"], "worktree" in result, first.exists()), ("done", False, False))
        self.assertNotIn("worktree", self.stored()["tasks"][0])
        self.assertEqual(result["commit"], git(self.root, "rev-parse", "--short", "HEAD"))
        self.assertEqual(git(self.root, "show", "--name-only", "--format=", "HEAD"),
                         "one.txt\nspecs/login/progress.json")
        self.move("T2", "review", "real-testing", "done")
        self.assertEqual(self.subjects(), ["login T2: Hash the password", "login T1: Reject an empty password",
                                           "base", "initial"])
        self.assertEqual((git(self.root, "status", "--porcelain"), git(self.root, "branch", "--show-current")),
                         ("", "feature/login"))
        self.assertEqual(sorted(path.name for path in self.root.glob("*.txt")), ["app.txt", "one.txt", "two.txt"])
        self.assertEqual((git(self.root, "branch", "--list", "tdd/*"), second.exists()), ("", False))
        self.assertFalse((self.root / ".worktrees").exists())

    def test_done_sends_a_merge_conflict_back_to_dev_with_the_conflict_as_note(self):
        self.develop("T1", "app.txt", "one\n")
        tree = self.develop("T2", "app.txt", "two\n")
        self.move("T1", "review", "real-testing", "done")
        head = git(self.root, "rev-parse", "HEAD")
        result, run = self.move("T2", "review", "real-testing", "done")
        self.assertEqual((result["status"], result["rejections"], result["escalate"]), ("dev", 1, False))
        self.assertEqual(result["note"], "app.txt: merge conflict with the last commit of the project root -> in the "
                         f"worktree .worktrees/login/T2, run `git merge {head}`, keep the work of both sides and make "
                         "the tests pass")
        stored = self.stored()["tasks"][1]
        self.assertEqual((stored["status"], stored["note"]), ("dev", result["note"]))
        self.assertEqual((git(self.root, "rev-parse", "HEAD"), git(tree, "status", "--porcelain")), (head, ""))
        run.assert_not_called()
        subprocess.run(["git", "merge", head], cwd=tree, capture_output=True)
        (tree / "app.txt").write_text("one and two\n")
        self.assertEqual(self.move("T2", "review", "real-testing", "done")[0]["status"], "done")
        self.assertEqual((self.root / "app.txt").read_text(), "one and two\n")
        self.assertEqual(git(self.root, "status", "--porcelain", "--", ".", ":(exclude)specs"), "")

    def test_done_runs_the_tests_in_the_worktree_before_the_root_changes(self):
        tree = self.develop("T1", "one.txt", "1\n")
        self.move("T1", "review", "real-testing")
        self.refused("failed in the worktree .worktrees/login/T1", self.move, "T1", "done", tests=FAIL)
        self.refused("test_lock ... FAILED", self.move, "T1", "done", tests=FAIL)
        self.assertEqual((self.subjects()[0], tree.exists()), ("base", True))
        self.assertEqual(self.stored()["tasks"][0]["status"], "real-testing")

    def test_done_can_be_asked_again_when_the_tests_fail_in_the_root_after_the_merge(self):
        self.develop("T1", "one.txt", "1\n")
        self.move("T1", "review", "real-testing")
        with patch.object(progress, "run_tests", side_effect=[PASS, FAIL]):
            self.refused("failed (exit 1)", progress.update, self.root, "login", "T1", "done", REAL_TEST)
        self.assertEqual((self.root / "one.txt").read_text(), "1\n")
        self.assertEqual(self.move("T1", "done")[0]["status"], "done")
        self.assertEqual(self.subjects()[:2], ["login T1: Reject an empty password", "base"])

    def test_done_can_be_asked_again_when_the_commit_fails_in_the_root_after_the_merge(self):
        tree = self.develop("T1", "one.txt", "1\n")
        self.move("T1", "review", "real-testing")
        self.refuse_every_commit()
        self.refused("lint failed", self.move, "T1", "done")
        self.assertEqual((self.stored()["tasks"][0]["status"], tree.exists()), ("real-testing", True))
        (self.root / ".git" / "hooks" / "pre-commit").unlink()
        self.assertEqual(self.move("T1", "done")[0]["status"], "done")
        self.assertEqual(self.subjects()[:2], ["login T1: Reject an empty password", "base"])

    def test_done_gives_the_commit_of_the_merge_when_the_root_has_nothing_more_to_commit(self):
        (self.root / ".gitignore").write_text("specs/\n")
        git(self.root, "add", "--all")
        git(self.root, "commit", "--quiet", "--message", "ignore the specs")
        self.develop("T1", "one.txt", "1\n")
        result, _ = self.move("T1", "review", "real-testing", "done")
        self.assertEqual(result["commit"], git(self.root, "rev-parse", "--short", "HEAD"))
        self.assertEqual(self.subjects()[:2], ["login T1: Reject an empty password", "ignore the specs"])

    def test_done_refuses_a_merge_that_git_cannot_start(self):
        tree = self.develop("T1", "one.txt", "1\n")
        self.move("T1", "review", "real-testing")
        git(tree, "checkout", "--quiet", "--orphan", "other")
        git(tree, "commit", "--quiet", "-m", "no common history")
        self.refused("unrelated histories", self.move, "T1", "done")
        self.assertEqual(self.subjects()[0], "base")

    def test_dev_refuses_a_task_with_no_worktree_while_another_task_has_one(self):
        self.move("T1", "dev")
        (self.root / "notes.txt").write_text("not committed\n")
        self.refused("stays new: it gets no worktree (uncommitted changes outside specs/: notes.txt",
                     self.move, "T2", "dev")
        self.assertEqual(self.stored()["tasks"][1]["status"], "new")

    def test_done_commits_the_specs_folder_of_the_root_with_the_evidence_of_the_worktree(self):
        tree = self.develop("T1", "one.txt", "1\n")
        evidence = Path("specs/login/real-testing/T1/output.txt")
        (tree / evidence).parent.mkdir(parents=True)
        (tree / evidence).write_text("what the real tester saw\n")
        (tree / "specs/login/spec.md").write_text("old copy\n")
        (self.root / "specs/login/spec.md").write_text("the spec\n")
        self.move("T1", "review", "real-testing", "done")
        self.assertEqual((self.root / evidence).read_text(), "what the real tester saw\n")
        self.assertEqual(git(self.root, "show", "HEAD:specs/login/spec.md"), "the spec")
        self.assertEqual(git(self.root, "show", "--format=", "--name-only", "HEAD").splitlines(), [
            "one.txt", "specs/login/progress.json", f"{evidence}", "specs/login/spec.md"])
        self.assertEqual(git(self.root, "status", "--porcelain"), "")

    def test_done_after_a_conflict_is_not_stopped_by_the_evidence_that_another_task_committed(self):
        self.create(tasks=[{**task, "depends_on": []} for task in TASKS])
        self.develop("T1", "app.txt", "one\n")
        tree = self.develop("T2", "app.txt", "two\n")
        self.develop("T3", "three.txt", "3\n")
        evidence = Path("specs/login/real-testing/T2/output.txt")
        (tree / evidence).parent.mkdir(parents=True)
        (tree / evidence).write_text("what the real tester saw\n")
        self.move("T1", "review", "real-testing", "done")
        self.assertEqual(self.move("T2", "review", "real-testing", "done")[0]["status"], "dev")
        self.move("T3", "review", "real-testing", "done")
        self.assertEqual(git(self.root, "show", f"HEAD:{evidence}"), "what the real tester saw")
        subprocess.run(["git", "merge", git(self.root, "rev-parse", "HEAD")], cwd=tree, capture_output=True)
        (tree / "app.txt").write_text("one and two\n")
        self.assertEqual(self.move("T2", "review", "real-testing", "done")[0]["status"], "done")
        self.assertEqual(((self.root / "app.txt").read_text(), git(self.root, "status", "--porcelain")),
                         ("one and two\n", ""))

    def test_done_refuses_a_worktree_that_holds_no_change(self):
        self.move("T1", "dev", "review", "real-testing")
        self.refused("holds no change", self.move, "T1", "done")
        self.assertEqual(self.stored()["tasks"][0]["status"], "real-testing")

    def test_refuses_to_run_from_inside_a_worktree(self):
        tree = self.develop("T1", "one.txt", "1\n")
        self.refused("from the project root", progress.next_tasks, tree, "login")
        self.refused("from the project root", progress.update, tree, "login", "T1", "review")


class StatusTest(Base):
    def test_counts_and_remaining(self):
        self.create()
        self.finish("T1")
        self.move("T2", "dev", "review", "dev", note="No test for the empty string.")
        result = progress.status(self.root, "login")
        self.assertEqual(result["counts"], {"new": 1, "dev": 1, "review": 0, "real-testing": 0, "done": 1})
        self.assertEqual((result["remaining"], result["finished"], result["status"]), (["T2", "T3"], False, "open"))
        self.assertEqual(result["tasks"], {"T1": "done", "T2": "dev", "T3": "new"})
        self.assertEqual(result["rejections"], {"T1": 0, "T2": 1, "T3": 0})

    def test_lists_every_feature(self):
        self.create()
        self.create(feature="signup", tasks=TASKS[:1])
        self.assertEqual([s["feature"] for s in progress.status(self.root)], ["login", "signup"])


class DashboardTest(Base):
    def test_shows_every_feature_and_task_with_status_and_rejections(self):
        self.create()
        self.create(feature="signup", tasks=TASKS[:1])
        self.finish("T1")
        self.move("T2", "dev", "review", "dev", note="No test for the empty string.")
        self.assertEqual(progress.dashboard(self.root).splitlines(), [
            "login (open): 1 of 3 tasks done",
            "  TASK  STATUS  REJECTIONS  TITLE",
            "  T1    done    0           Reject an empty password",
            "  T2    dev     1           Hash the password",
            "  T3    new     0           Lock after 3 failures",
            "",
            "signup (open): 0 of 1 tasks done",
            "  TASK  STATUS  REJECTIONS  TITLE",
            "  T1    new     0           Reject an empty password",
        ])

    def test_shows_one_feature_and_marks_a_task_rejected_3_times(self):
        self.create()
        self.create(feature="signup", tasks=TASKS[:1])
        self.move("T1", "dev", "review", "dev", "review", "dev", "review", "dev", note="Wrong.")
        lines = progress.dashboard(self.root, "login").splitlines()
        self.assertEqual(lines[:3], [
            "login (open): 0 of 3 tasks done",
            "  TASK  STATUS          REJECTIONS  TITLE",
            "  T1    dev, escalated  3           Reject an empty password",
        ])
        self.assertEqual(len(lines), 5)

    def test_says_when_there_is_no_feature_and_refuses_an_unknown_one(self):
        self.assertEqual(progress.dashboard(self.root), "No feature: specs/ holds no progress.json.")
        self.refused("no progress file", progress.dashboard, self.root, "login")


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
        self.finish("T1")
        self.assertEqual(self.verify()[0], [])
        self.assertEqual(self.stored()["status"], "closed")
        self.verify()[1].assert_not_called()
        self.refused("closed", self.create, tasks=TASKS[:1])

    def test_reports_failing_tests_and_keeps_the_feature_open(self):
        self.create(tasks=TASKS[:1])
        self.finish("T1")
        lines, _ = self.verify(tests=FAIL)
        self.assertEqual(lines[0], "FAIL: login: test command failed: run-tests")
        self.assertIn("test_lock ... FAILED", lines[1])
        self.assertEqual(self.stored()["status"], "open")


class CloseTest(GitBase, VerifyTest):
    def test_closing_commits_the_progress_file_only(self):
        self.create(tasks=TASKS[:1])
        self.finish("T1")
        (self.root / "notes.txt").write_text("not for the commit\n")
        self.assertEqual(self.verify()[0], [])
        self.assertEqual(self.subjects()[0], "login: closed")
        self.assertEqual(git(self.root, "show", "--name-only", "--format=", "HEAD"), "specs/login/progress.json")
        self.assertEqual(git(self.root, "status", "--porcelain"), "?? notes.txt")

    def test_keeps_the_feature_open_when_the_closing_commit_fails(self):
        self.create(tasks=TASKS[:1])
        self.finish("T1")
        self.refuse_every_commit()
        self.assertTrue(self.verify()[0][0].startswith("FAIL: login: the commit failed"))
        self.assertEqual(self.stored()["status"], "open")


class PullRequestTest(GitBase):
    URL = "https://github.com/owner/project/pull/7"

    def pull_request(self, tests=PASS, opened=(0, URL)):
        with patch.object(progress, "run_tests", return_value=tests), \
                patch.object(progress, "open_pull_request", return_value=opened) as opener:
            return progress.pull_request(self.root, "login"), opener

    def test_closes_the_feature_pushes_the_branch_and_opens_the_pull_request(self):
        self.create(tasks=ALONE)
        self.finish("T1")
        self.finish("T2")
        result, opener = self.pull_request()
        self.assertEqual(result, {"feature": "login", "branch": "feature/login", "url": self.URL})
        self.assertEqual(self.stored()["status"], "closed")
        self.assertEqual(self.subjects("feature/login", self.remote), [
            "login: closed", "login T2: Hash the password", "login T1: Reject an empty password", "initial"])
        self.assertEqual(self.subjects("main", self.remote), ["initial"])
        (root, branch, title, body), _ = opener.call_args
        self.assertEqual((root, branch, title), (self.root, "feature/login", "login"))
        for text in ("specs/login/spec.md", "- T1: Reject an empty password", "- T2: Hash the password", "run-tests"):
            self.assertIn(text, body)

    def test_refuses_an_unfinished_feature_and_pushes_nothing(self):
        self.create(tasks=ALONE)
        self.finish("T1")
        self.refused("login: task T2 is 'new', not 'done'", self.pull_request)
        self.finish("T2")
        self.refused("login: test command failed: run-tests\n  test_lock ... FAILED", self.pull_request, tests=FAIL)
        self.assertEqual((self.stored()["status"], git(self.remote, "branch", "--list", "feature/*")), ("open", ""))

    def test_refuses_to_push_the_default_branch_of_the_remote(self):
        git(self.root, "checkout", "--quiet", "-b", "work")
        git(self.root, "push", "--quiet", "origin", "work")
        git(self.remote, "symbolic-ref", "HEAD", "refs/heads/work")
        self.create(tasks=TASKS[:1])
        self.finish("T1")
        self.refused("default branch 'work'", self.pull_request)
        self.assertEqual(self.subjects("work", self.remote), ["initial"])

    def test_refuses_without_a_remote_and_still_closes_the_feature(self):
        git(self.root, "remote", "remove", "origin")
        self.create(tasks=TASKS[:1])
        self.finish("T1")
        self.refused("no pull request: the remote 'origin'", self.pull_request)
        self.assertEqual((self.stored()["status"], self.subjects()[0]), ("closed", "login: closed"))

    def test_says_that_the_branch_is_pushed_when_the_pull_request_cannot_be_opened(self):
        self.create(tasks=TASKS[:1])
        self.finish("T1")
        self.refused("the branch 'feature/login' is pushed, but the pull request is not open: gh: not found",
                     self.pull_request, opened=(1, "gh: not found"))
        self.assertEqual(self.subjects("feature/login", self.remote)[0], "login: closed")

    def test_refuses_outside_git(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        self.root = Path(outside.name)
        self.create(tasks=TASKS[:1])
        self.finish("T1")
        self.refused("not on a branch of a git repository", self.pull_request)

    def test_opens_the_pull_request_with_the_github_command_line(self):
        tools = self.root / "tools"
        tools.mkdir()
        (tools / "gh").write_text(f'#!/bin/sh\necho "$@" > called.txt\necho "{self.URL}"\n')
        (tools / "gh").chmod(0o755)
        with patch.dict(os.environ, {"PATH": f"{tools}{os.pathsep}{os.environ['PATH']}"}):
            result = progress.open_pull_request(self.root, "feature/login", "login", "the body")
        self.assertEqual(result, (0, self.URL))
        self.assertEqual((self.root / "called.txt").read_text().strip(),
                         "pr create --head feature/login --title login --body the body")


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
        code, out, _ = self.run_cli("status", "login", "--json")
        self.assertEqual(json.loads(out)["remaining"], ["T1", "T2", "T3"])

    def test_status_prints_the_dashboard(self):
        self.run_cli("create", "login", "--test-command", "true", stdin=json.dumps(TASKS[:1]))
        for arguments in (("status",), ("status", "login")):
            code, out, _ = self.run_cli(*arguments)
            self.assertEqual((code, out), (0, "login (open): 0 of 1 tasks done\n"
                                              "  TASK  STATUS  REJECTIONS  TITLE\n"
                                              "  T1    new     0           Reject an empty password\n"))
        code, out, _ = self.run_cli("status", "--json")
        self.assertEqual((code, json.loads(out)[0]["rejections"]), (0, {"T1": 0}))

    def test_pr_prints_the_pull_request_or_the_refusal(self):
        self.run_cli("create", "login", "--test-command", "true", stdin=json.dumps(TASKS[:1]))
        code, out, err = self.run_cli("pr", "login")
        self.assertEqual((code, out, err), (1, "", "ERROR: login: task T1 is 'new', not 'done'\n"))
        with patch.object(progress, "pull_request", return_value={"url": "https://example.com/pull/1"}) as opener:
            code, out, _ = self.run_cli("pr", "login")
        self.assertEqual((code, json.loads(out)["url"]), (0, "https://example.com/pull/1"))
        opener.assert_called_once_with(str(self.root), "login")

    def test_error_goes_to_stderr_with_exit_code_1(self):
        code, out, err = self.run_cli("update", "login", "T1", "dev")
        self.assertEqual((code, out), (1, ""))
        self.assertTrue(err.startswith("ERROR: "))

    def test_verify_runs_the_real_test_command(self):
        self.run_cli("create", "login", "--test-command", "echo boom && exit 3", stdin=json.dumps(TASKS[:1]))
        self.run_cli("update", "login", "T1", "dev")
        self.run_cli("update", "login", "T1", "review")
        self.run_cli("update", "login", "T1", "real-testing", "--note", REVIEW)
        code, _, err = self.run_cli("update", "login", "T1", "done", "--note", REAL_TEST)
        self.assertEqual(code, 1)
        self.assertIn("boom", err)
        code, out, _ = self.run_cli("verify")
        self.assertEqual(code, 1)
        self.assertIn("FAIL: login: task T1 is 'real-testing', not 'done'", out)


if __name__ == "__main__":
    unittest.main()
