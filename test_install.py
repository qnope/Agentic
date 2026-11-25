import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import install_lib

SKILL = """---
name: plan
description: Plans. Use when asked to plan.
---
The worker is the agent `agents/worker.md`. Run `python3 mcp-servers/tracker/tool.py next`.
A template path such as `agents/<name>.md` or `agents/missing.md` installs nothing.
"""
WORKFLOW = """# Workflow: loop

plan -> build

## Components
- plan: skill `skills/plan/SKILL.md`
- build: skill `skills/build/SKILL.md`, gate `hooks/gate.py`
"""
HOOK = """import sys
print("FAIL: not finished", file=sys.stderr)
sys.exit(0 if '"stop_hook_active": true' in sys.stdin.read() else 2)
"""
# The record of an installed folder: the files that the last install wrote in it.
RECORD = ".agentic-installed"


class FakeRun:
    """Stands for subprocess.run: keeps the commands, and creates the python of a new environment."""

    def __init__(self):
        self.commands, self.failing = [], None

    def __call__(self, command, **options):
        self.commands.append(command)
        if command[1:3] == ["-m", "venv"]:
            python = Path(command[3]) / install_lib.PYTHON
            python.parent.mkdir(parents=True)
            python.write_text("")
        failed = self.failing in command if self.failing else False
        return subprocess.CompletedProcess(command, 1 if failed else 0, "", "no network" if failed else "")


class Base(unittest.TestCase):
    def setUp(self):
        self.run_command = FakeRun()
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.source, self.project = Path(folder.name) / "repo", Path(folder.name) / "project"
        for path, text in {
            "skills/plan/SKILL.md": SKILL, "skills/plan/Steps.md": "steps", "skills/plan/test/scenarios_1.md": "s",
            "skills/build/SKILL.md": "Build.", "agents/worker.md": "worker", "agents/other.md": "other",
            "hooks/gate.py": HOOK, "hooks/test_gate.py": "tests",
            "mcp-servers/tracker/server.py": "server", "mcp-servers/tracker/tool.py": "tool",
            "mcp-servers/tracker/requirements.txt": "mcp", "mcp-servers/tracker/test_tool.py": "tests",
            "workflows/loop.md": WORKFLOW,
        }.items():
            (self.source / path).parent.mkdir(parents=True, exist_ok=True)
            (self.source / path).write_text(text)
        self.project.mkdir()

    def install(self, tool, *parts, project=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = install_lib.main(tool, [*parts, "--project", str(project or self.project)], source=self.source,
                                    run=self.run_command)
        return code, out.getvalue(), err.getvalue()

    def files(self):
        """The files of the project, without the Python environments and the records of the installed folders."""
        return sorted(str(p.relative_to(self.project)) for p in self.project.rglob("*")
                      if p.is_file() and ".venv" not in p.parts and p.name != RECORD)

    def json(self, path):
        return json.loads((self.project / path).read_text())


class ClaudeTest(Base):
    def test_skill_goes_to_the_tool_folder_without_its_tests_and_brings_what_it_names(self):
        code, out, _ = self.install("claude", "skill/plan")
        self.assertEqual(code, 0)
        self.assertEqual(self.files(), [
            ".claude/agents/worker.md", ".claude/skills/plan/SKILL.md", ".claude/skills/plan/Steps.md", ".gitignore",
            ".mcp.json", "mcp-servers/tracker/requirements.txt", "mcp-servers/tracker/server.py",
            "mcp-servers/tracker/tool.py",
        ])
        self.assertEqual(self.json(".mcp.json"), {"mcpServers": {"tracker": {
            "command": "mcp-servers/tracker/.venv/bin/python", "args": ["mcp-servers/tracker/server.py"]}}})
        self.assertIn("created mcp-servers/tracker/.venv", out)

    def test_agent_alone(self):
        self.assertEqual(self.install("claude", "agent/other")[0], 0)
        self.assertEqual(self.files(), [".claude/agents/other.md", ".gitignore"])

    def test_hook_is_copied_and_registered_once_and_other_settings_are_kept(self):
        (self.project / ".claude").mkdir()
        (self.project / ".claude/settings.json").write_text('{"permissions": {"allow": ["Read"]}}')
        self.install("claude", "hook/gate")
        self.install("claude", "hook/gate")
        self.assertEqual(self.files(), [".claude/settings.json", ".gitignore", "hooks/gate.py"])
        self.assertEqual(self.json(".claude/settings.json"), {
            "permissions": {"allow": ["Read"]},
            "hooks": {"Stop": [{"hooks": [{"type": "command",
                                           "command": 'cd "$CLAUDE_PROJECT_DIR" && python3 hooks/gate.py'}]}]},
        })

    def test_workflow_installs_every_component(self):
        code, out, _ = self.install("claude", "workflow/loop")
        self.assertEqual(code, 0)
        for path in (".claude/skills/plan/SKILL.md", ".claude/skills/build/SKILL.md", ".claude/agents/worker.md",
                     "hooks/gate.py", "mcp-servers/tracker/server.py", ".mcp.json", ".claude/settings.json"):
            self.assertIn(path, self.files())
        self.assertNotIn(".claude/agents/other.md", self.files())
        self.assertFalse((self.project / "workflows").exists())

    def test_installed_text_names_the_installed_paths(self):
        self.install("claude", "skill/plan")
        text = (self.project / ".claude/skills/plan/SKILL.md").read_text()
        self.assertIn("the agent `.claude/agents/worker.md`. Run `python3 mcp-servers/tracker/tool.py next`", text)
        self.assertIn("`agents/<name>.md` or `agents/missing.md`", text)

    def test_folder_names_and_file_paths_are_accepted_and_several_parts(self):
        self.assertEqual(self.install("claude", "agents/other.md", "skills/build/")[0], 0)
        self.assertEqual(self.files(), [".claude/agents/other.md", ".claude/skills/build/SKILL.md", ".gitignore"])

    def test_says_what_changed(self):
        self.assertIn("created .claude/agents/other.md", self.install("claude", "agent/other")[1])
        self.assertIn("unchanged .claude/agents/other.md", self.install("claude", "agent/other")[1])
        (self.source / "agents/other.md").write_text("new text")
        self.assertIn("updated .claude/agents/other.md", self.install("claude", "agent/other")[1])
        self.assertEqual((self.project / ".claude/agents/other.md").read_text(), "new text")
        self.install("claude", "skill/plan")
        (self.source / "skills/plan/Steps.md").write_text("new steps")  # A reference file of a skill.
        out = self.install("claude", "skill/plan")[1].splitlines()
        self.assertIn("updated .claude/skills/plan/Steps.md", out)
        self.assertIn("unchanged .claude/skills/plan/SKILL.md", out)
        self.assertEqual((self.project / ".claude/skills/plan/Steps.md").read_text(), "new steps")

    def test_unknown_part_installs_nothing_and_lists_the_names(self):
        code, _, err = self.install("claude", "agent/other", "skill/nope")
        self.assertEqual((code, self.files()), (1, []))
        self.assertIn("unknown skill 'nope'", err)
        self.assertIn("build, plan", err)
        code, _, err = self.install("claude", "plugin/x")
        self.assertEqual(code, 1)
        self.assertIn("skill, agent, hook, workflow, mcp-server", err)

    def test_without_a_part_lists_the_parts_and_installs_nothing(self):
        code, out, _ = self.install("claude")
        self.assertEqual((code, self.files()), (0, []))
        for part in ("skill/build", "skill/plan", "agent/worker", "hook/gate", "workflow/loop", "mcp-server/tracker"):
            self.assertIn(part, out.split())
        self.assertNotIn("hook/test_gate", out)

    def test_skill_and_agent_of_the_claude_folder_of_the_repository(self):
        for path in (".claude/skills/make/SKILL.md", ".claude/agents/runner.md"):
            (self.source / path).parent.mkdir(parents=True, exist_ok=True)
            (self.source / path).write_text("Start the agent `.claude/agents/runner.md`.")
        self.assertEqual(self.install("cursor", "skill/make")[0], 0)
        self.assertEqual(self.files(), [".cursor/agents/runner.md", ".cursor/skills/make/SKILL.md", ".gitignore"])
        self.assertIn("`.cursor/agents/runner.md`", (self.project / ".cursor/skills/make/SKILL.md").read_text())

    def test_refuses_a_config_file_that_is_not_json(self):
        (self.project / ".mcp.json").write_text("{not json")
        code, _, err = self.install("claude", "mcp-server/tracker")
        self.assertEqual(code, 1)
        self.assertIn(".mcp.json", err)
        self.assertEqual(self.files(), [".mcp.json"])
        self.assertEqual((self.project / ".mcp.json").read_text(), "{not json")
        (self.project / ".mcp.json").write_text('{"mcpServers": []}')
        self.assertEqual(self.install("claude", "mcp-server/tracker")[0], 1)
        self.assertEqual(self.files(), [".mcp.json"])

    def test_installs_into_the_repository_itself(self):
        code, out, _ = self.install("claude", "workflow/loop", project=self.source)
        self.assertEqual(code, 0)
        self.assertIn("unchanged hooks/gate.py", out)
        self.assertEqual((self.source / "hooks/gate.py").read_text(), HOOK)
        self.assertTrue((self.source / ".claude/skills/plan/SKILL.md").exists())
        self.assertFalse((self.source / "mcp-servers/tracker" / RECORD).exists())


class UpdateTest(Base):
    def test_new_install_removes_the_files_that_the_part_no_longer_has(self):
        (self.source / "skills/plan/refs").mkdir()
        (self.source / "skills/plan/refs/old.md").write_text("old")
        self.install("claude", "skill/plan")
        (self.source / "skills/plan/Steps.md").rename(self.source / "skills/plan/Stages.md")
        shutil.rmtree(self.source / "skills/plan/refs")
        (self.source / "mcp-servers/tracker/tool.py").unlink()
        code, out, _ = self.install("claude", "skill/plan")
        self.assertEqual(code, 0)
        for line in ("removed .claude/skills/plan/Steps.md", "removed .claude/skills/plan/refs/old.md",
                     "created .claude/skills/plan/Stages.md", "removed mcp-servers/tracker/tool.py"):
            self.assertIn(line, out.splitlines())
        self.assertEqual(self.files(), [
            ".claude/agents/worker.md", ".claude/skills/plan/SKILL.md", ".claude/skills/plan/Stages.md", ".gitignore",
            ".mcp.json", "mcp-servers/tracker/requirements.txt", "mcp-servers/tracker/server.py",
        ])
        self.assertFalse((self.project / ".claude/skills/plan/refs").exists())

    def test_new_install_removes_only_the_files_that_an_install_wrote(self):
        self.install("claude", "skill/plan")
        mine = [".claude/skills/plan/notes.md", "mcp-servers/tracker/data.json", ".claude/agents/mine.md"]
        for path in mine:
            (self.project / path).write_text("mine")
        with open(self.project / ".claude/skills/plan" / RECORD, "a") as file:
            file.write("../../agents/mine.md\n")  # A record never removes a file outside its folder.
        (self.source / "skills/plan/Steps.md").unlink()
        out = self.install("claude", "skill/plan")[1]
        self.assertEqual([line for line in out.splitlines() if line.startswith("removed")],
                         ["removed .claude/skills/plan/Steps.md"])
        for path in mine:
            self.assertEqual((self.project / path).read_text(), "mine")
        self.assertTrue((self.project / "mcp-servers/tracker/.venv" / install_lib.PYTHON).exists())

    def test_installed_part_that_the_repository_no_longer_has_is_not_touched(self):
        self.install("claude", "workflow/loop")
        self.install("cursor", "hook/gate")
        (self.source / "hooks/gate.py").rename(self.source / "hooks/check.py")
        (self.source / "agents/worker.md").rename(self.source / "agents/helper.md")
        shutil.rmtree(self.source / "skills/build")
        shutil.rmtree(self.source / "mcp-servers/tracker")
        before = {path: (self.project / path).read_bytes() for path in self.files()}
        code, out, _ = self.install("claude", "skill/plan")
        self.assertEqual(code, 0)
        self.assertEqual([line for line in out.splitlines() if line.startswith("not touched")], [
            "not touched .claude/agents/worker.md: this repository has no agent 'worker'",
            "not touched .claude/skills/build/: this repository has no skill 'build'",
            "not touched .cursor/hooks/gate.py: this repository has no hook 'gate'",
            "not touched hooks/gate.py: this repository has no hook 'gate'",
            "not touched mcp-servers/tracker/: this repository has no mcp-server 'tracker'",
        ])
        self.assertEqual({path: (self.project / path).read_bytes() for path in self.files()}, before)
        shutil.rmtree(self.project / "mcp-servers/tracker")  # A part deleted by hand is not named again.
        self.assertNotIn("tracker", self.install("claude", "skill/plan")[1])


class CursorTest(Base):
    def test_workflow_uses_the_cursor_folders_and_config_files(self):
        self.assertEqual(self.install("cursor", "workflow/loop")[0], 0)
        self.assertEqual(self.files(), [
            ".cursor/agents/worker.md", ".cursor/hooks.json", ".cursor/hooks/gate.py", ".cursor/mcp.json",
            ".cursor/skills/build/SKILL.md", ".cursor/skills/plan/SKILL.md", ".cursor/skills/plan/Steps.md",
            ".gitignore", "hooks/gate.py", "mcp-servers/tracker/requirements.txt", "mcp-servers/tracker/server.py",
            "mcp-servers/tracker/tool.py",
        ])
        self.assertEqual(self.json(".cursor/mcp.json"), {"mcpServers": {"tracker": {
            "type": "stdio", "command": "${workspaceFolder}/mcp-servers/tracker/.venv/bin/python",
            "args": ["${workspaceFolder}/mcp-servers/tracker/server.py"],
            "env": {"TRACKER_ROOT": "${workspaceFolder}"}}}})
        self.assertEqual(self.json(".cursor/hooks.json"), {
            "version": 1, "hooks": {"stop": [{"command": "python3 .cursor/hooks/gate.py"}]}})

    def test_hook_is_registered_once_and_other_hooks_are_kept(self):
        (self.project / ".cursor").mkdir()
        (self.project / ".cursor/hooks.json").write_text(
            '{"version": 1, "hooks": {"afterFileEdit": [{"command": "./format.sh"}]}}')
        self.install("cursor", "hook/gate")
        self.install("cursor", "hook/gate")
        self.assertEqual(self.json(".cursor/hooks.json"), {"version": 1, "hooks": {
            "afterFileEdit": [{"command": "./format.sh"}], "stop": [{"command": "python3 .cursor/hooks/gate.py"}]}})

    def adapter(self, stdin):
        done = subprocess.run([sys.executable, ".cursor/hooks/gate.py"], input=stdin, cwd=self.project,
                              capture_output=True, text=True)
        return done.returncode, json.loads(done.stdout)

    def test_adapter_turns_a_blocked_stop_into_a_follow_up_message(self):
        self.install("cursor", "hook/gate")
        self.assertEqual(self.adapter('{"status": "completed", "loop_count": 0}'),
                         (0, {"followup_message": "FAIL: not finished"}))

    def test_adapter_lets_the_agent_stop_after_a_follow_up_or_an_abort_or_bad_input(self):
        self.install("cursor", "hook/gate")
        self.assertEqual(self.adapter('{"status": "completed", "loop_count": 1}'), (0, {}))
        self.assertEqual(self.adapter('{"status": "aborted", "loop_count": 0}'), (0, {}))
        self.assertEqual(self.adapter("not json")[0], 0)


class EnvironmentTest(Base):
    def setUp(self):
        super().setUp()
        self.venv = self.project / "mcp-servers/tracker/.venv"
        self.pip = [str(self.venv / install_lib.PYTHON), "-m", "pip", "install", "-r",
                    str(self.project / "mcp-servers/tracker/requirements.txt")]

    def test_server_with_requirements_gets_an_environment_with_them(self):
        code, out, _ = self.install("claude", "mcp-server/tracker")
        self.assertEqual(code, 0)
        self.assertEqual(self.run_command.commands, [[sys.executable, "-m", "venv", str(self.venv)], self.pip])
        self.assertIn("created mcp-servers/tracker/.venv", out)
        self.assertNotIn("Still to do", out)
        self.assertEqual((self.venv / ".gitignore").read_text(), "*\n")

    def test_second_install_keeps_the_environment_and_changed_requirements_update_it(self):
        self.install("claude", "mcp-server/tracker")
        self.run_command.commands.clear()
        self.assertIn("unchanged mcp-servers/tracker/.venv", self.install("claude", "mcp-server/tracker")[1])
        self.assertEqual(self.run_command.commands, [])
        (self.source / "mcp-servers/tracker/requirements.txt").write_text("mcp>=3")
        self.assertIn("updated mcp-servers/tracker/.venv", self.install("claude", "mcp-server/tracker")[1])
        self.assertEqual(self.run_command.commands, [self.pip])

    def test_failed_pip_installs_the_rest_exits_with_1_and_the_next_install_tries_again(self):
        self.run_command.failing = "pip"
        code, out, err = self.install("claude", "skill/plan")
        self.assertEqual(code, 1)
        self.assertIn("pip install -r", err)
        self.assertIn("no network", err)
        self.assertIn("created .claude/skills/plan/SKILL.md", out)
        self.assertIn(".mcp.json", self.files())
        self.assertIn(".gitignore", self.files())
        self.run_command.failing = None
        self.run_command.commands.clear()
        self.assertEqual(self.install("claude", "skill/plan")[0], 0)
        self.assertEqual(self.run_command.commands, [self.pip])

    def test_server_without_requirements_runs_with_python3_and_gets_no_environment(self):
        (self.source / "mcp-servers/tracker/requirements.txt").unlink()
        self.assertEqual(self.install("claude", "mcp-server/tracker")[0], 0)
        self.assertEqual(self.run_command.commands, [])
        self.assertEqual(self.json(".mcp.json")["mcpServers"]["tracker"]["command"], "python3")

    def test_environment_of_the_repository_is_not_copied(self):
        (self.source / "mcp-servers/tracker/.venv").mkdir()
        (self.source / "mcp-servers/tracker/.venv/pyvenv.cfg").write_text("home = /usr/bin")
        self.install("claude", "mcp-server/tracker")
        self.assertFalse((self.venv / "pyvenv.cfg").exists())

    def test_real_environment_is_created_and_its_python_is_the_registered_command(self):
        (self.source / "mcp-servers/tracker/requirements.txt").write_text("# nothing to install\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = install_lib.main("claude", ["mcp-server/tracker", "--project", str(self.project)], source=self.source)
        self.assertEqual(code, 0)
        python = self.json(".mcp.json")["mcpServers"]["tracker"]["command"]
        done = subprocess.run([python, "-c", "import sys; print(sys.prefix)"], cwd=self.project,
                              capture_output=True, text=True)
        self.assertEqual(Path(done.stdout.strip()).resolve(), self.venv.resolve())


class GitignoreTest(Base):
    def gitignore(self, project=None):
        return ((project or self.project) / ".gitignore").read_text()

    def block(self, *paths):
        """The block of the install in `.gitignore`, with these paths."""
        return "\n".join(["# >>> Agentic: paths written by install_claude.py and install_cursor.py >>>", *paths,
                          "# <<< Agentic <<<"]) + "\n"

    def seen_by_git(self):
        """The files of the project that git does not ignore. The ignore file of the user of the machine is not read."""
        subprocess.run(["git", "init", "--quiet"], cwd=self.project, check=True)
        done = subprocess.run(["git", "-c", f"core.excludesFile={self.project / 'none'}", "status", "--porcelain",
                               "--untracked-files=all"], cwd=self.project, capture_output=True, text=True, check=True)
        return sorted(line[3:] for line in done.stdout.splitlines())

    def test_git_ignores_everything_that_the_install_wrote(self):
        code, out, _ = self.install("claude", "workflow/loop")
        self.assertEqual(code, 0)
        self.assertIn("created .gitignore", out)
        self.assertEqual(self.gitignore(), self.block(
            "/.claude/agents/worker.md", "/.claude/settings.json", "/.claude/skills/build/", "/.claude/skills/plan/",
            "/.mcp.json", "/hooks/gate.py", "/mcp-servers/tracker/"))
        self.assertEqual(self.seen_by_git(), [".gitignore"])

    def test_next_installs_add_their_paths_once_to_the_same_block(self):
        self.install("claude", "agent/other")
        self.assertIn("unchanged .gitignore", self.install("claude", "agent/other")[1])
        self.assertEqual(self.gitignore(), self.block("/.claude/agents/other.md"))
        self.assertIn("updated .gitignore", self.install("cursor", "workflow/loop")[1])
        self.assertEqual(self.gitignore(), self.block(
            "/.claude/agents/other.md", "/.cursor/agents/worker.md", "/.cursor/hooks.json", "/.cursor/hooks/gate.py",
            "/.cursor/mcp.json", "/.cursor/skills/build/", "/.cursor/skills/plan/", "/hooks/gate.py",
            "/mcp-servers/tracker/"))

    def test_lines_and_files_of_the_user_are_kept_and_git_still_sees_them(self):
        mine = [".claude/agents/mine.md", ".claude/skills/mine/SKILL.md", "hooks/mine.py", "mcp-servers/mine/server.py"]
        for path in mine:
            (self.project / path).parent.mkdir(parents=True, exist_ok=True)
            (self.project / path).write_text("mine")
        (self.project / ".gitignore").write_text("build/\n*.log")
        self.install("claude", "agent/other")
        with open(self.project / ".gitignore", "a") as file:
            file.write("\n# mine\ndist/\n")
        self.install("claude", "workflow/loop")
        self.assertEqual(self.gitignore(), "build/\n*.log\n\n" + self.block(
            "/.claude/agents/other.md", "/.claude/agents/worker.md", "/.claude/settings.json", "/.claude/skills/build/",
            "/.claude/skills/plan/", "/.mcp.json", "/hooks/gate.py", "/mcp-servers/tracker/") + "\n# mine\ndist/\n")
        self.assertEqual(self.seen_by_git(), sorted([*mine, ".gitignore"]))

    def test_config_file_is_ignored_only_when_it_holds_nothing_but_what_the_install_writes(self):
        (self.project / ".claude").mkdir()
        (self.project / ".claude/settings.json").write_text('{"permissions": {"allow": ["Read"]}}')
        out = self.install("claude", "hook/gate", "mcp-server/tracker")[1]
        self.assertIn("not ignored .claude/settings.json", out)
        self.assertNotIn("not ignored .mcp.json", out)
        self.assertEqual(self.gitignore(), self.block("/.mcp.json", "/hooks/gate.py", "/mcp-servers/tracker/"))
        # A config file of an install that wrote no `.gitignore` holds nothing of the user: it is ignored.
        (self.project / ".claude/settings.json").unlink()
        self.install("claude", "hook/gate")
        (self.project / ".gitignore").unlink()
        self.assertNotIn("not ignored", self.install("claude", "hook/gate")[1])
        self.assertEqual(self.gitignore(), self.block("/.claude/settings.json", "/hooks/gate.py"))

    def test_parts_of_the_repository_itself_are_not_ignored(self):
        (self.source / ".claude/skills/make").mkdir(parents=True)
        (self.source / ".claude/skills/make/SKILL.md").write_text("Make.")
        self.assertEqual(self.install("claude", "workflow/loop", "skill/make", project=self.source)[0], 0)
        self.assertEqual(self.gitignore(self.source), self.block(
            "/.claude/agents/worker.md", "/.claude/settings.json", "/.claude/skills/build/", "/.claude/skills/plan/",
            "/.mcp.json"))


class EntryScriptTest(Base):
    def test_each_script_installs_for_its_tool_into_the_current_folder(self):
        for script, folder in (("install_claude.py", ".claude"), ("install_cursor.py", ".cursor")):
            done = subprocess.run([sys.executable, str(Path(__file__).resolve().parent / script), "agent/tdd-reviewer"],
                                  cwd=self.project, capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertTrue((self.project / folder / "agents/tdd-reviewer.md").exists())


if __name__ == "__main__":
    unittest.main()
