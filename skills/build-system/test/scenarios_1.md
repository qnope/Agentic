# Scenario 1: Happy path, a C++ project without build system gets a CMake build for Linux, macOS and Windows, with its settings on its targets

## Prompt
Create a build system for this project.

## Setup
Create `README.md` with this exact content:

````
# calc

A small C++ library.
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

Then run in the scratch directory: `git init -b main`, `git add -A` and `git -c user.name=test -c user.email=test@example.com commit -m init`.

## Pass criteria
- [ ] `CMakeLists.txt` exists at the root. It contains `cmake_minimum_required`, and it declares the C++ standard on a target: it contains `cxx_std_` (`target_compile_features`) or the target property `CXX_STANDARD`.
- [ ] No `CMakeLists.txt` of the project sets a global variable: none contains `set(CMAKE_`, `CMAKE_CXX_FLAGS`, `/usr` or `Release` (a default build type `Release` switches off the `assert` of the test). If one contains a compiler option that starts with `-W` or `/W` (`-Wall`, `/W4`), it also contains `MSVC` or `CXX_COMPILER_ID`: the option is chosen for the compiler.
- [ ] No `CMakeLists.txt` of the project calls a command that acts on every target: `include_directories(`, `add_compile_options(`, `add_definitions(`, `add_compile_definitions(`, `link_libraries(` or `link_directories(` (a command whose name starts with `target_` is not one of these). The include folder is given to a target: a `CMakeLists.txt` contains `target_include_directories(`.
- [ ] `README.md` holds three commands: a `cmake` command with `-B <folder>`, a `cmake --build` command that contains `--config`, and a `ctest` command that contains `-C ` or `--build-config`. (Without them, `ctest` runs no test on Windows.)
- [ ] Run in the scratch directory, in the order of `README.md`, the three commands exit with code 0. The output of `ctest` contains `100% tests passed` and does not contain `No tests were found`.
- [ ] `git check-ignore -q <folder>/CMakeCache.txt` exits with code 0: the build folder of the commands is ignored.
- [ ] After the commands, `git status --porcelain` lists only `README.md`, `.gitignore` and files named `CMakeLists.txt`: no build output is visible to git, and no other file was created or changed.
- [ ] `include/calc.h`, `src/calc.cpp` and `tests/calc_test.cpp` have the exact Setup content.
- [ ] The final output says that the commands were run locally and passed (it contains `passed`), and that they were not run on macOS and not run on Windows (it names both).

## RED baseline (without the skill)
2026-11-22 — FAIL (3 of 3 runs failed) — all 3 wrote a `Makefile` with `g++` and `-Wall -Wextra -O2` instead of a CMake build ("cmake seemed too heavy"): it does not build on Windows. All 3 added `.gitignore` with `build/`. 2 runs did not write the commands in `README.md`. No run said that the build was not run on macOS and Windows.
2026-11-22 — FAIL (2 of 3 runs failed) — with the skill as it was before the rule "no global variable". The 3 runs wrote a CMake build and gave the include folder to the target `calc`. 2 runs set the global variables `CMAKE_CXX_STANDARD` and `CMAKE_CXX_STANDARD_REQUIRED` (1 also `CMAKE_CXX_EXTENSIONS`): the skill named `CMAKE_CXX_STANDARD`. 1 run used `target_compile_features` and passed: the test agents of this run knew the request of the human partner ("no global variable"), their tool gave it to them.
