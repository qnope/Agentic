"""Install parts of this repository into a project, for one coding tool (`claude` or `cursor`).

Used by install_claude.py and install_cursor.py:
    ./install_claude.py <kind>/<name> [<kind>/<name> ...] [--project <folder>]
<kind> is skill, agent, hook, workflow or mcp-server. Without --project, the project is the current folder.
A part brings the parts of this repository that its text names by path: `skills/<name>/SKILL.md`,
`agents/<name>.md`, `hooks/<name>.py`, `mcp-servers/<name>/`. A workflow installs all its components.
An MCP server that has a `requirements.txt` gets its own Python environment, `mcp-servers/<name>/.venv`,
with these requirements installed in it. The tool starts the server with the Python of this environment.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Where a part is in this repository. `{}` is its name.
WHERE = {
    "skill": ("skills/{}/SKILL.md", ".claude/skills/{}/SKILL.md"),
    "agent": ("agents/{}.md", ".claude/agents/{}.md"),
    "hook": ("hooks/{}.py",),
    "workflow": ("workflows/{}.md",),
    "mcp-server": ("mcp-servers/{}/server.py",),
}
FOLDERS = ("skill", "mcp-server")  # These parts are a whole folder. The others are one file.
# How a text names another part.
NAMED = {"skill": r"skills/([\w-]+)/SKILL\.md", "agent": r"agents/([\w-]+)\.md",
         "hook": r"hooks/([\w-]+)\.py", "mcp-server": r"mcp-servers/([\w-]+)/"}

# The Python of an environment, from the folder of the environment.
PYTHON = Path("Scripts/python.exe" if os.name == "nt" else "bin/python")

# Cursor continues the agent with a follow-up message, not with exit code 2: this script translates.
CURSOR_ADAPTER = '''#!/usr/bin/env python3
"""Cursor stop hook, written by install_cursor.py. Cursor runs it from the project root.

It runs hooks/{name}.py. If that hook blocks the stop (exit code 2), its message becomes the
follow-up message that makes the agent continue. After one follow-up, the agent is free to stop.
"""
import json
import subprocess
import sys

HOOK = [sys.executable, "hooks/{name}.py"]


def main():
    try:
        data = json.load(sys.stdin)
        again = data.get("status") != "completed" or data.get("loop_count", 0) > 0
    except (ValueError, AttributeError):
        print("{{}}")
        return 0
    done = subprocess.run(HOOK, input=json.dumps({{"stop_hook_active": again}}), capture_output=True, text=True)
    print(json.dumps({{"followup_message": done.stderr.strip()}} if done.returncode == 2 else {{}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


class InstallError(Exception):
    """The installation cannot be done. Nothing was written."""


def find(source, kind, name):
    """Return the path of a part in the repository (its folder for a skill or a server), or None."""
    for pattern in WHERE[kind]:
        path = source / pattern.format(name)
        if path.is_file() and not name.startswith("test_"):
            return path.parent if kind in FOLDERS else path
    return None


def available(source, kind):
    """Return the names of the parts of one kind that the repository has."""
    names = set()
    for pattern in WHERE[kind]:
        for path in source.glob(pattern.format("*")):
            names.add(path.parent.name if kind in FOLDERS else path.stem)
    return sorted(name for name in names if not name.startswith("test_"))


def parse(source, text):
    """Turn `skill/plan` into ("skill", "plan"). Also accepts `skills/plan/` and `agents/worker.md`."""
    kind, _, name = text.partition("/")
    kind = kind if kind in WHERE else kind.removesuffix("s")
    if kind not in WHERE:
        raise InstallError(f"unknown kind in '{text}'. Write <kind>/<name>. The kinds are: {', '.join(WHERE)}")
    name = re.sub(r"(/SKILL\.md|\.md|\.py|/)$", "", name)
    if not find(source, kind, name):
        names = ", ".join(available(source, kind)) or "none"
        raise InstallError(f"unknown {kind} '{name}'. The {kind}s of this repository are: {names}")
    return kind, name


def kept(folder):
    """Return the files of a skill or server folder that a project needs: no tests, no caches, no hidden files."""
    files = []
    for path in sorted(folder.rglob("*")):
        inside = path.relative_to(folder)
        skipped = ({"test", "__pycache__"} & set(inside.parts[:-1]) or path.name.startswith("test_")
                   or any(part.startswith(".") for part in inside.parts))
        if path.is_file() and not skipped:
            files.append(inside)
    return files


def with_named_parts(source, wanted):
    """Return the wanted parts, then the parts that their texts name, each one once."""
    parts, queue = [], list(wanted)
    while queue:
        part = queue.pop(0)
        if part in parts:
            continue
        parts.append(part)
        kind, name = part
        path = find(source, kind, name)
        texts = [] if kind == "mcp-server" else [path / inside for inside in kept(path)] if kind == "skill" else [path]
        for text in texts:
            content = text.read_text(errors="replace")
            for other, pattern in NAMED.items():
                queue += [(other, found) for found in re.findall(pattern, content) if find(source, other, found)]
    return parts


def child(parent, key, empty, path):
    """Return parent[key], created empty if absent. Refuse a value of another type."""
    value = parent.setdefault(key, empty)
    if type(value) is not type(empty):
        raise InstallError(f'{path}: "{key}" must be {"a list" if isinstance(empty, list) else "an object"}')
    return value


def plan(tool, source, project, parts):
    """Return (files, configs, servers): what to write in the project, and the servers that need an environment.

    Writes nothing.
    """
    home = f".{tool}"
    files, configs, servers = {}, {}, []

    def config(path):
        if path not in configs:
            try:
                configs[path] = json.loads((project / path).read_text()) if (project / path).exists() else {}
            except ValueError as error:
                raise InstallError(f"{path} is not valid JSON ({error}). Fix it or delete it, then install again")
            if not isinstance(configs[path], dict):
                raise InstallError(f"{path} must contain a JSON object. Fix it or delete it, then install again")
        return configs[path]

    def text(path):
        """Read a file. In a markdown file, make the paths of the installed skills and agents right."""
        content = path.read_bytes()
        if path.suffix == ".md":
            content = content.decode()
            for kind, name in parts:
                if kind in ("skill", "agent"):
                    named = f"skills/{name}/" if kind == "skill" else f"agents/{name}.md"
                    content = re.sub(rf"(?<![\w./-])(?:\.claude/)?{re.escape(named)}", f"{home}/{named}", content)
            content = content.encode()
        return content

    for kind, name in parts:
        path = find(source, kind, name)
        if kind == "skill":
            for inside in kept(path):
                files[f"{home}/skills/{name}/{inside.as_posix()}"] = text(path / inside)
        elif kind == "agent":
            files[f"{home}/agents/{name}.md"] = text(path)
        elif kind == "hook":
            files[f"hooks/{name}.py"] = path.read_bytes()
            if tool == "claude":
                command = f'cd "$CLAUDE_PROJECT_DIR" && python3 hooks/{name}.py'
                settings = config(".claude/settings.json")
                groups = child(child(settings, "hooks", {}, ".claude/settings.json"), "Stop", [], ".claude/settings.json")
                if not any(hook.get("command") == command for group in groups for hook in group.get("hooks", [])):
                    groups.append({"hooks": [{"type": "command", "command": command}]})
            else:
                files[f".cursor/hooks/{name}.py"] = CURSOR_ADAPTER.format(name=name).encode()
                command = f"python3 .cursor/hooks/{name}.py"
                hooks = config(".cursor/hooks.json")
                hooks.setdefault("version", 1)
                entries = child(child(hooks, "hooks", {}, ".cursor/hooks.json"), "stop", [], ".cursor/hooks.json")
                if not any(entry.get("command") == command for entry in entries):
                    entries.append({"command": command})
        elif kind == "mcp-server":
            for inside in kept(path):
                files[f"mcp-servers/{name}/{inside.as_posix()}"] = (path / inside).read_bytes()
            python = "python3"
            if (path / "requirements.txt").exists():
                servers.append(name)
                python = f"mcp-servers/{name}/.venv/{PYTHON.as_posix()}"
            if tool == "claude":
                entry = {"command": python, "args": [f"mcp-servers/{name}/server.py"]}
            else:
                entry = {"type": "stdio", "command": python if python == "python3" else "${workspaceFolder}/" + python,
                         "args": [f"${{workspaceFolder}}/mcp-servers/{name}/server.py"],
                         "env": {name.upper().replace("-", "_") + "_ROOT": "${workspaceFolder}"}}
            path_of_config = ".mcp.json" if tool == "claude" else ".cursor/mcp.json"
            child(config(path_of_config), "mcpServers", {}, path_of_config)[name] = entry
    return files, configs, servers


def write(project, path, content, same):
    """Write one file of the project. Return created, updated or unchanged."""
    target = project / path
    if target.exists() and same(target.read_bytes()):
        return "unchanged"
    state = "updated" if target.exists() else "created"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return state


def environment(folder, run):
    """Give a server folder its Python environment `.venv`, with its requirements installed.

    Return created, updated or unchanged. `.venv/requirements.txt` keeps the requirements that are installed.
    """
    venv, wanted = folder / ".venv", (folder / "requirements.txt").read_bytes()
    python, installed = venv / PYTHON, venv / "requirements.txt"
    if python.exists() and installed.exists() and installed.read_bytes() == wanted:
        return "unchanged"
    state = "updated" if python.exists() else "created"
    commands = [] if python.exists() else [[sys.executable, "-m", "venv", str(venv)]]
    commands.append([str(python), "-m", "pip", "install", "-r", str(folder / "requirements.txt")])
    for command in commands:
        done = run(command, capture_output=True, text=True)
        if done.returncode != 0:
            output = "\n".join((done.stdout + done.stderr).splitlines()[-15:])
            raise InstallError(f"this command failed (exit {done.returncode}): {' '.join(command)}\n{output}\n"
                               "The rest is installed. Fix the cause, then run the install again")
    (venv / ".gitignore").write_text("*\n")
    installed.write_bytes(wanted)
    return state


def install(tool, source, project, wanted, run=subprocess.run):
    """Install the wanted parts and the parts they name. Yield one line for each thing done."""
    if not project.is_dir():
        raise InstallError(f"the project folder does not exist: {project}")
    parts = with_named_parts(source, [parse(source, text) for text in wanted])
    files, configs, servers = plan(tool, source, project, [part for part in parts if part[0] != "workflow"])
    for path, content in files.items():
        yield f"{write(project, path, content, content.__eq__)} {path}"
    for path, value in configs.items():
        content = (json.dumps(value, indent=2) + "\n").encode()
        yield f"{write(project, path, content, lambda old, value=value: json.loads(old) == value)} {path}"
    for name in servers:
        yield f"{environment(project / 'mcp-servers' / name, run)} mcp-servers/{name}/.venv"


def main(tool, argv=None, source=None, run=subprocess.run):
    source = Path(source or Path(__file__).resolve().parent)
    parser = argparse.ArgumentParser(
        prog=f"install_{tool}.py",
        description=f"Install parts of this repository into a project, in the format of {tool}.")
    parser.add_argument("parts", nargs="*", metavar="<kind>/<name>",
                        help=f"a part to install. <kind> is one of: {', '.join(WHERE)}")
    parser.add_argument("--project", default=".", help="the project folder (default: the current folder)")
    options = parser.parse_args(argv)
    if not options.parts:
        parser.print_usage()
        print("The parts of this repository are:")
        for kind in WHERE:
            print("\n".join(f"  {kind}/{name}" for name in available(source, kind)))
        return 0
    try:
        for line in install(tool, source, Path(options.project).resolve(), options.parts, run):
            print(line, flush=True)
    except InstallError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0
