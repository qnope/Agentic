import contextlib
import io
import json
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


class Base(unittest.TestCase):
    def setUp(self):
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
            code = install_lib.main(tool, [*parts, "--project", str(project or self.project)], source=self.source)
        return code, out.getvalue(), err.getvalue()

    def files(self):
        return sorted(str(p.relative_to(self.project)) for p in self.project.rglob("*") if p.is_file())

    def json(self, path):
        return json.loads((self.project / path).read_text())


class ClaudeTest(Base):
    def test_skill_goes_to_the_tool_folder_without_its_tests_and_brings_what_it_names(self):
        code, out, _ = self.install("claude", "skill/plan")
        self.assertEqual(code, 0)
        self.assertEqual(self.files(), [
            ".claude/agents/worker.md", ".claude/skills/plan/SKILL.md", ".claude/skills/plan/Steps.md", ".mcp.json",
            "mcp-servers/tracker/requirements.txt", "mcp-servers/tracker/server.py", "mcp-servers/tracker/tool.py",
        ])
        self.assertEqual(self.json(".mcp.json"), {"mcpServers": {"tracker": {
            "command": "python3", "args": ["mcp-servers/tracker/server.py"]}}})
        self.assertIn("pip install -r mcp-servers/tracker/requirements.txt", out)

    def test_agent_alone(self):
        self.assertEqual(self.install("claude", "agent/other")[0], 0)
        self.assertEqual(self.files(), [".claude/agents/other.md"])

    def test_hook_is_copied_and_registered_once_and_other_settings_are_kept(self):
        (self.project / ".claude").mkdir()
        (self.project / ".claude/settings.json").write_text('{"permissions": {"allow": ["Read"]}}')
        self.install("claude", "hook/gate")
        self.install("claude", "hook/gate")
        self.assertEqual(self.files(), [".claude/settings.json", "hooks/gate.py"])
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
        self.assertEqual(self.files(), [".claude/agents/other.md", ".claude/skills/build/SKILL.md"])

    def test_says_what_changed(self):
        self.assertIn("created .claude/agents/other.md", self.install("claude", "agent/other")[1])
        self.assertIn("unchanged .claude/agents/other.md", self.install("claude", "agent/other")[1])
        (self.source / "agents/other.md").write_text("new text")
        self.assertIn("updated .claude/agents/other.md", self.install("claude", "agent/other")[1])
        self.assertEqual((self.project / ".claude/agents/other.md").read_text(), "new text")

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
        self.assertEqual(self.files(), [".cursor/agents/runner.md", ".cursor/skills/make/SKILL.md"])
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


class CursorTest(Base):
    def test_workflow_uses_the_cursor_folders_and_config_files(self):
        self.assertEqual(self.install("cursor", "workflow/loop")[0], 0)
        self.assertEqual(self.files(), [
            ".cursor/agents/worker.md", ".cursor/hooks.json", ".cursor/hooks/gate.py", ".cursor/mcp.json",
            ".cursor/skills/build/SKILL.md", ".cursor/skills/plan/SKILL.md", ".cursor/skills/plan/Steps.md",
            "hooks/gate.py", "mcp-servers/tracker/requirements.txt", "mcp-servers/tracker/server.py",
            "mcp-servers/tracker/tool.py",
        ])
        self.assertEqual(self.json(".cursor/mcp.json"), {"mcpServers": {"tracker": {
            "type": "stdio", "command": "python3", "args": ["${workspaceFolder}/mcp-servers/tracker/server.py"],
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


class EntryScriptTest(Base):
    def test_each_script_installs_for_its_tool_into_the_current_folder(self):
        for script, folder in (("install_claude.py", ".claude"), ("install_cursor.py", ".cursor")):
            done = subprocess.run([sys.executable, str(Path(__file__).resolve().parent / script), "agent/tdd-reviewer"],
                                  cwd=self.project, capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertTrue((self.project / folder / "agents/tdd-reviewer.md").exists())


if __name__ == "__main__":
    unittest.main()
