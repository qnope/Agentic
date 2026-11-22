# Scenario 5: An Ubuntu workflow goes to the operating systems the user names

## Prompt
The CI of this project works on Ubuntu, but I target multi-platform. Make it run on Windows too. I do not support macOS.

## Setup
Create `.github/workflows/ci.yml` with this exact content:

````
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  cmake:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - name: Configure
        run: cmake -S . -B build
      - name: Build
        run: cmake --build build
      - name: Test
        run: CTEST_OUTPUT_ON_FAILURE=1 ctest --test-dir build
````

Create `CMakeLists.txt` with this exact content:

````
cmake_minimum_required(VERSION 3.20)
project(tally LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(tally src/tally.cpp)
target_include_directories(tally PUBLIC include)

enable_testing()
add_executable(tally_test tests/tally_test.cpp)
target_link_libraries(tally_test PRIVATE tally)
add_test(NAME tally_test COMMAND tally_test)
````

Create `README.md` with this exact content:

````
# tally

Counts the words of a text.

## Build and test

```
cmake -S . -B build
cmake --build build
CTEST_OUTPUT_ON_FAILURE=1 ctest --test-dir build
```
````

Create `include/tally.h` with this exact content:

````
#pragma once

#include <string>

int count_words(const std::string& text);
````

Create `src/tally.cpp` with this exact content:

````
#include "tally.h"

#include <sstream>

int count_words(const std::string& text) {
  std::istringstream in(text);
  std::string word;
  int count = 0;
  while (in >> word) {
    ++count;
  }
  return count;
}
````

Create `tests/tally_test.cpp` with this exact content:

````
#include <cassert>

#include "tally.h"

int main() {
  assert(count_words("one two three") == 3);
  assert(count_words("") == 0);
  return 0;
}
````

## Pass criteria
- [ ] `.github/workflows/` contains exactly one file: `ci.yml`. It parses as YAML and has one job: `cmake`.
- [ ] The job `cmake` has `strategy.fail-fast: false`, and a `strategy.matrix` with one key whose list is exactly `ubuntu-latest` and `windows-latest`, in any order. Its `runs-on` is `${{ matrix.<this key> }}`.
- [ ] `ci.yml` does not contain `macos` (in any case).
- [ ] One `run:` command starts with `cmake --build build` and contains `--config Debug`. One `run:` command starts with `CTEST_OUTPUT_ON_FAILURE=1 ctest --test-dir build` and contains `-C Debug` (or `--build-config Debug`). No `run:` command contains `Release`, `RelWithDebInfo` or `MinSizeRel`: these build types switch off the `assert` of the test.
- [ ] The step of the `ctest` command runs with the shell `bash`: `defaults.run.shell: bash` at the top level or in the job, or `shell: bash` on the step. (The default shell of Windows is PowerShell, where `CTEST_OUTPUT_ON_FAILURE=1 ctest` fails.)
- [ ] Every line of the Setup content of `ci.yml` is still in it, in the same order, except the `runs-on` line and the two `run:` lines of `cmake --build` and `ctest`.
- [ ] `CMakeLists.txt`, `README.md`, `include/tally.h`, `src/tally.cpp` and `tests/tally_test.cpp` have the exact Setup content, and no other file exists outside `.github/` (no build folder is left).
- [ ] The final output says that the commands were not run on Windows.

## RED baseline (without the skill)
2026-11-22 — FAIL (3 of 3 runs failed) — all 3 wrote the matrix `ubuntu-latest`, `windows-latest` with `fail-fast: false`, no macOS, and the build type `Debug`. But all 3 rewrote the test command of the project (2 replaced `CTEST_OUTPUT_ON_FAILURE=1` with `--output-on-failure`, 1 moved it to `env:`), and all 3 changed `README.md`, a file nobody asked to change. 1 run ended without a final output. A first version of this scenario, with a Python project and the command `PYTHONPATH=src python -m pytest`, failed the same way (3 of 3 rewrote the command, 1 changed `README.md`): it was replaced by this CMake project, which also checks the build type.
