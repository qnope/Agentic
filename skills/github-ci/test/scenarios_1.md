# Scenario 1: Happy path, a CMake project gets its CI workflow

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
#include "calc.h"

int main() { return add(2, 3) == 5 ? 0 : 1; }
````

Then run in the scratch directory: `git init -b develop`, `git add -A` and `git -c user.name=test -c user.email=test@example.com commit -m init`.

## Pass criteria
- [ ] `.github/workflows/ci.yml` exists, parses as YAML, and is the only file under `.github/`.
- [ ] The workflow has the trigger `pull_request`, and the trigger `push` whose `branches` list is exactly `develop`.
- [ ] The top-level `permissions` is exactly `contents: read`.
- [ ] The top-level `concurrency` has `cancel-in-progress: true`.
- [ ] Every job has `timeout-minutes`, and no job has `strategy` (no matrix).
- [ ] The `run:` commands hold, in this order: a `cmake` configure command that contains `-DCALC_BUILD_TESTS=ON`, a `cmake --build` command, and a `ctest` command that contains `--output-on-failure`.
- [ ] `git status --porcelain` prints exactly one line: `?? .github/` (no build folder is left, no other file was created or changed).
- [ ] The final output contains the text `ctest` and says that the commands were run locally and passed (it contains `passed`).

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — all 3 wrote `branches: [main]` while the default branch is `develop`, so the CI never runs on a push. No run set `timeout-minutes`, 2 runs had no `concurrency`, and 2 runs added a matrix of 3 operating systems that the project does not ask for. All 3 took the configure option from the README and ran the commands locally.
