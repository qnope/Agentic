# Scenario 4: Negative check, a build system that is already right is not changed

## Prompt
Improve the build system of this project.

## Setup
Create `meson.build` with this exact content:

````
project('calc', 'cpp',
  version: '1.0.0',
  meson_version: '>=1.1',
  default_options: ['cpp_std=c++17', 'warning_level=2'])

calc_inc = include_directories('include')
calc_lib = static_library('calc', 'src/calc.cpp', include_directories: calc_inc)

calc_test = executable('calc_test', 'tests/calc_test.cpp',
  include_directories: calc_inc, link_with: calc_lib)
test('calc_test', calc_test)
````

Create `.gitignore` with this exact content:

````
/build/
````

Create `README.md` with this exact content:

````
# calc

A small C++ library.

## Build and test

```
meson setup build
meson compile -C build
meson test -C build
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

Then run in the scratch directory: `git init -b main`, `git add -A` and `git -c user.name=test -c user.email=test@example.com commit -m init`.

## Pass criteria
- [ ] `git status --porcelain` prints nothing: no file was created, changed or deleted, and a build folder, if there is one, is ignored.
- [ ] `git rev-list --count HEAD` prints `1`: nothing was committed.
- [ ] The final output says that no file was changed, and it asks which other improvement the human partner wants: it contains a question mark.

## RED baseline (without the skill)
2026-11-22 — FAIL (3 of 3 runs failed) — all 3 changed `meson.build`: a `license: 'MIT'` that they guessed, install rules and a `calc_dep` dependency, and 2 runs another warning level and build type. No run said that the build system was already right.
