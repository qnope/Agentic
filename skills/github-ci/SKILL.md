---
name: github-ci
description: Creates or adapts the GitHub Actions workflow that builds and tests a project on each push and pull request. It detects the build system (CMake, Python, Node.js, Rust, Go, Make, ...) from the project files and runs the commands of the project. Use when the user asks to add, create, set up or change a GitHub CI, a GitHub Actions workflow or a CI pipeline on GitHub.
---

# GitHub CI

Writes the workflow that builds and tests the project on GitHub Actions. It changes the workflow file and nothing else.

## Rules (no exceptions, even if the human partner asks)
1. **The commands of the project only.** Every `run:` command comes from the project (Step 1). Never invent a check. If the project has nothing to build and no test: create no file, and ask which commands the CI must run.
2. **A failure stays red.** Never hide a failure: no `continue-on-error`, no `|| true`, no `set +e`, no test skipped, deselected, deleted or changed. If a command fails, write the workflow with the real command. In the report, name what fails and say that the CI fails until it is fixed.
3. **The workflow file only.** Change no source file, no test and no config file of the project. Leave no build output in the project.
4. **One CI workflow.** If a file of `.github/workflows/` already builds, tests or lints the project, change this file: only add lines, keep every existing line as it is. Otherwise create `.github/workflows/ci.yml`.

## Step 1 — Find the commands
Look for the build and test commands in this order. The first source that gives them wins:
1. What the project documents: `README`, `CONTRIBUTING`, a `Makefile` target, the `scripts` of `package.json`, `CMakePresets.json`. Copy the commands with their options.
2. The standard commands of the build system:

| File | Setup | Commands |
|---|---|---|
| `CMakeLists.txt` | none | `cmake -S . -B build`, `cmake --build build`, `ctest --test-dir build --output-on-failure` |
| `pyproject.toml`, `requirements*.txt` | `actions/setup-python` | `python -m pip install -r <requirements file>` or `python -m pip install .`, then `python -m pytest` |
| `package.json` | `actions/setup-node` | `npm ci`, then `npm run <script>` for each script `lint` and `build` that exists, then `npm test` |
| other (`Cargo.toml`, `go.mod`, ...) | the setup action of the language | the standard build and test commands of this build system |

The version of the language comes from the project (`.nvmrc`, `.python-version`, `requires-python`, `go.mod`, an existing job). Several build systems: one job for each.

## Step 2 — Write the workflow
A new workflow has exactly this frame:

```yaml
name: CI

on:
  push:
    branches: [<default branch>]
  pull_request:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  <build system>:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v<N>
      - name: <what the command does>
        run: <one command>
```

- `<default branch>`: read it, do not guess it. `git symbolic-ref --short refs/remotes/origin/HEAD`, and if there is no remote, `git branch --show-current`. Only if the project is not a git repository: `main`.
- One step for each command.
- No `strategy` and no matrix, unless the project names several versions or operating systems to support.
- An action is named with a major version tag (`@v<N>`), never with a branch.
- A job added to an existing workflow follows the existing jobs (runner, action versions, language version) and has `timeout-minutes`.

## Step 3 — Check
1. Run each `run:` command, in the order of the workflow, on a copy of the project in a temporary folder outside the project. Delete the copy afterwards. If a tool is not installed, the command is `not run`.
2. Parse the workflow file as YAML.
3. Check that the version control status shows only the workflow file as changed. If the project is not a git repository, list its files instead.

## Step 4 — Report
- The workflow file, and the build system found.
- Each command with its local result: `passed`, `failed` or `not run`.
- What fails (Rule 2), and that the workflow did not run on GitHub yet.
