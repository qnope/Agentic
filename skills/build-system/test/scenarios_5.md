# Scenario 5: A CMake build with global variables, that works with GCC on Linux only, gets its settings on its targets, is made portable, and its test runs with ctest

## Prompt
Improve the build system of this project.

## Setup
Create `CMakeLists.txt` with this exact content:

````
cmake_minimum_required(VERSION 3.16)
project(tally CXX)

set(CMAKE_CXX_COMPILER g++)
set(CMAKE_CXX_FLAGS "-std=c++17 -Wall -Wextra")

include_directories(include)

add_library(tally src/tally.cpp)

add_executable(tally_test tests/tally_test.cpp)
target_link_libraries(tally_test tally)
````

Create `.gitignore` with this exact content:

````
build/
````

Create `README.md` with this exact content:

````
# tally

Counts the words of a text.

## Build and test

```
mkdir build && cd build
cmake ..
make
./tally_test
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

Then run in the scratch directory: `git init -b main`, `git add -A` and `git -c user.name=test -c user.email=test@example.com commit -m init`.

## Pass criteria
- [ ] `CMakeLists.txt` sets no global variable: it does not contain `set(CMAKE_` (no compiler, no flags, no standard, no build type), `-std=` or `Release` (a default build type `Release` switches off the `assert` of the test). It declares the standard C++17 on a target: it contains `cxx_std_17` (`target_compile_features`) or the target property `CXX_STANDARD 17`.
- [ ] `CMakeLists.txt` calls no command that acts on every target: `include_directories(`, `add_compile_options(`, `add_definitions(`, `add_compile_definitions(`, `link_libraries(` or `link_directories(` (a command whose name starts with `target_` is not one of these). It contains `target_include_directories(` and `target_compile_options(`.
- [ ] `CMakeLists.txt` still contains `-Wall` and `-Wextra`, and it contains `MSVC` or `CXX_COMPILER_ID`: the warnings are kept, and chosen for the compiler.
- [ ] `CMakeLists.txt` contains `add_test`, and `enable_testing` or `include(CTest)`. It still contains `add_library(tally` and `add_executable(tally_test`: the targets are kept.
- [ ] `README.md` holds three commands: a `cmake` command with `-B <folder>`, a `cmake --build` command that contains `--config`, and a `ctest` command that contains `-C ` or `--build-config`. It has no line that is exactly `make`, and it does not contain `./tally_test`.
- [ ] Run in the scratch directory, after `<folder>` is deleted, in the order of `README.md`, the three commands exit with code 0. The output of `ctest` contains `100% tests passed` and does not contain `No tests were found`.
- [ ] After the commands, `git status --porcelain` lists only `CMakeLists.txt` and `README.md`: no build output is visible to git, and no other file was created or changed.
- [ ] `.gitignore`, `include/tally.h`, `src/tally.cpp` and `tests/tally_test.cpp` have the exact Setup content.
- [ ] The final output says that the commands were run locally and passed (it contains `passed`), and that they were not run on macOS and not run on Windows (it names both).

## RED baseline (without the skill)
2026-11-22 — FAIL (3 of 3 runs failed) — all 3 removed the hardcoded compiler, declared C++17 with `CMAKE_CXX_STANDARD` and registered the test with `add_test`. But all 3 made `Release` the default build type: the `assert` of the test is switched off, so the test passes without checking anything. 2 runs kept `-Wall -Wextra` for every compiler (MSVC rejects them). No run gave `--config` and `-C` to the commands of `README.md`, and 1 run wrote commands that run inside the build folder. No run said that the commands were not run on macOS and Windows.
2026-11-22 — FAIL (3 of 3 runs failed) — with the skill as it was before the rule "no global variable". All 3 set the global variables `CMAKE_CXX_STANDARD` and `CMAKE_CXX_STANDARD_REQUIRED`. 2 runs kept `include_directories(include)` and gave the warnings to every target with `add_compile_options` ("the four points of the skill do not cover it"). 1 run used `target_include_directories` and `target_compile_options`.
