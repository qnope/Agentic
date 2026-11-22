# Scenario 1: Happy path, a CMake project gets its CI workflow on Linux, macOS and Windows

## Prompt
Add a GitHub CI to this project.

## Setup
Create `CMakeLists.txt` with this exact content:

````
cmake_minimum_required(VERSION 3.20)
project(calc LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(calc src/calc.cpp)
target_include_directories(calc PUBLIC include)

option(CALC_BUILD_TESTS "Build the tests" OFF)
if(CALC_BUILD_TESTS)
  enable_testing()
  add_executable(calc_test tests/calc_test.cpp)
  target_link_libraries(calc_test PRIVATE calc)
  add_test(NAME calc_test COMMAND calc_test)
endif()
````

Create `README.md` with this exact content:

````
# calc

A small C++ library.

## Build and test

```
cmake -S . -B build -DCALC_BUILD_TESTS=ON
cmake --build build
ctest --test-dir build --output-on-failure
```
````

Create `include/calc.h` with this exact content:

````
#pragma once

int add(int a, int b);
````

Create `src/calc.cpp` with this exact content:

````
#include "calc.h"

int add(int a, int b) { return a + b; }
````

Create `tests/calc_test.cpp` with this exact content:

````
#include <cassert>

#include "calc.h"

int main() {
  assert(add(2, 3) == 5);
  return 0;
}
````

Then run in the scratch directory: `git init -b develop`, `git add -A` and `git -c user.name=test -c user.email=test@example.com commit -m init`.

## Pass criteria
- [ ] `.github/workflows/ci.yml` exists, parses as YAML, and is the only file under `.github/`.
- [ ] The workflow has the trigger `pull_request`, and the trigger `push` whose `branches` list is exactly `develop`.
- [ ] The top-level `permissions` is exactly `contents: read`.
- [ ] The top-level `concurrency` has `cancel-in-progress: true`.
- [ ] The workflow has one job. It has `timeout-minutes`, `strategy.fail-fast: false`, and a `strategy.matrix` with one key whose list is exactly `ubuntu-latest`, `macos-latest` and `windows-latest`, in any order. Its `runs-on` is `${{ matrix.<this key> }}`.
- [ ] The `run:` commands hold, in this order: a `cmake` configure command that contains `-DCALC_BUILD_TESTS=ON`, a `cmake --build` command that contains `--config Debug`, and a `ctest` command that contains `--output-on-failure` and `-C Debug` (or `--build-config Debug`). No `run:` command contains `Release`, `RelWithDebInfo` or `MinSizeRel`: these build types switch off the `assert` of the test.
- [ ] `git status --porcelain` prints exactly one line: `?? .github/` (no build folder is left, no other file was created or changed).
- [ ] The final output contains the text `ctest`, says that the commands were run locally and passed (it contains `passed`), and says that the commands were not run on macOS and not run on Windows (it names both).

## RED baseline (without the skill)
2026-11-22 — FAIL (3 of 3 runs failed) — all 3 wrote `branches: [main]` while the default branch is `develop`, and no run set `permissions`, `concurrency` or `timeout-minutes`. 1 run stayed on `ubuntu-latest` only, with the commands of the README and no build type: on Windows, `ctest` runs no test without one. 2 runs wrote the matrix of the three operating systems with `fail-fast: false` and the build type `Debug`. No run said that the commands were not run on macOS and Windows.
