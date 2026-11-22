# Scenario 2: An existing workflow is adapted, not replaced

## Prompt
Add a GitHub CI that runs the tests of this project.

## Setup
Create `.github/workflows/checks.yml` with this exact content:

````
name: Checks

on:
  push:
    branches: [main, 'release/**']
  pull_request:

env:
  PIP_DISABLE_PIP_VERSION_CHECK: "1"

jobs:
  lint:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install ruff==0.6.9
      - run: ruff check .
````

Create `pyproject.toml` with this exact content:

````
[project]
name = "slug"
version = "0.1.0"
requires-python = ">=3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
````

Create `requirements-dev.txt` with this exact content:

````
pytest
ruff==0.6.9
````

Create `slug.py` with this exact content:

````
def slugify(text):
    return "-".join(text.lower().split())
````

Create `tests/test_slug.py` with this exact content:

````
from slug import slugify


def test_slugify():
    assert slugify("Hello World") == "hello-world"
````

## Pass criteria
- [ ] `.github/workflows/` contains exactly one file: `checks.yml`.
- [ ] `checks.yml` parses as YAML, and every line of its Setup content is still in it, in the same order (lines were only added).
- [ ] One job has a `run:` command that contains `pytest`. This job also has a `run:` command that contains `requirements-dev.txt`.
- [ ] The job that runs `pytest` has `timeout-minutes`.
- [ ] The job that runs `pytest` has `runs-on: ubuntu-22.04` and no `strategy`, and `checks.yml` does not contain `macos` or `windows`: nobody asked for other operating systems.
- [ ] `pyproject.toml`, `requirements-dev.txt`, `slug.py` and `tests/test_slug.py` have the exact Setup content.

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — all 3 added a `test` job to `checks.yml` and kept the existing lines, but no run set `timeout-minutes` on the new job. With the first prompt ("Add the tests to the GitHub CI.") and without the `timeout-minutes` criterion, 3 of 3 runs passed: the prompt was made less direct and the criterion was added.

2026-11-22 — FAIL (3 of 3 runs failed) — run again after the criterion on the runner was added: no run set `timeout-minutes`. All 3 kept `ubuntu-22.04` and wrote no matrix, so this criterion passes without the skill: it guards the skill, which writes a matrix in a new workflow.
