---
name: build-system
description: Creates the build system of a project that has none, or improves the one it has (CMake, Cargo, npm, Meson, ...), so that the same commands build and test the project on Linux, macOS and Windows, no build folder is in git, and each setting belongs to a target, not to a global variable. Use when the user asks to create, add, set up, fix or improve a build system, a build, build files or build scripts (`CMakeLists.txt`, `Cargo.toml`, `package.json`, `meson.build`, `Makefile`), to make a build work on another operating system, to keep build folders out of git, or to remove global variables from a build.
---

# Build system

Makes the build system of the project meet five points, and changes nothing else:

1. **Commands.** `README.md` holds the commands that build and test the project. The same commands work on Linux, macOS and Windows.
2. **Build folders.** Git ignores every folder that the build writes, and tracks no file of these folders.
3. **Portable.** The build files hold nothing that works with one compiler, one shell or one machine only.
4. **No global variable.** Each setting of the build (include folder, compiler option, definition, version of the language) is given to the target that needs it. No global variable and no global command gives a setting to every target.
5. **Tests.** The test command of the build system runs the tests of the project.

## Rules (no exceptions, even if the human partner asks)
1. **No build folder in git.** A build folder is a folder that the build or its tools write: build output, downloaded dependencies, caches (`build/`, `target/`, `dist/`, `node_modules/`, ...). Never add one to git and never commit one. When the human partner asks for it: do not. In the report, say that a build folder is never committed, and name the other way that gives what they want: a cache of the CI for a faster build, a release for the built files.
2. **The build system of the project.** A project that has a build system keeps it: never replace it by another one, and keep the name and the job of every target, script and option. A project without build system gets the one of its language in the table, or the one the human partner names.
3. **The five points only.** Change only what breaks one of the five points. Add nothing that nobody asked for: no dependency, no option, no profile, no build type, no install rule, no metadata. When the build system already meets the five points, change no file.
4. **The build files only.** Change the build files, `.gitignore` and the build commands of `README.md`. Never change a source file or a test.

## Build systems

| Build system | Language | Build folders | Commands | Reference file |
|---|---|---|---|---|
| CMake, `CMakeLists.txt` | C, C++ | `build/` | `cmake -S . -B build`, `cmake --build build --config Debug`, `ctest --test-dir build -C Debug --output-on-failure` | `cmake.md` |
| Cargo, `Cargo.toml` | Rust | `target/` | `cargo build`, `cargo test` | `cargo.md` |
| npm, `package.json` | JavaScript, TypeScript | `node_modules/`, the folder that the script `build` writes | `npm ci`, `npm run build`, `npm test` | `npm.md` |
| Meson, `meson.build` | when the project uses it | the folder given to `meson setup` | `meson setup build`, `meson compile -C build`, `meson test -C build` | `meson.md` |
| other | the standard build system of the language | every folder that it writes | its standard commands | none |

A reference file holds the rules of one build system. It is in the folder of this file.

## Step 1 — Read
1. Read the reference file of the build system of the project. Its rules apply with the rules of this file.
2. Read the build files, the commands of `README.md`, `.gitignore` and the output of `git ls-files`. For each of the five points, note what breaks it.

## Step 2 — Change
**Commands.** Commands of `README.md` that already work on the three operating systems stay as they are. Otherwise write the commands of the table, in a code block.

**Build folders.**
- Add each build folder to `.gitignore`. Only add lines: every existing line stays.
- A build folder that git tracks: `git rm -r --cached <folder>`. Its files stay on the disk.
- A lock file (`Cargo.lock`, `package-lock.json`) is not build output: it stays in git.

**Portable.**
- No compiler and no absolute path in a build file (`/usr/...`).
- The build system declares the version of the language. A compiler option does not (`-std=`).
- A compiler option goes only to the compilers that know it.
- No command of a POSIX shell in a script or a custom command: `rm`, `cp`, `mkdir -p` and `VAR=value command` fail on Windows. Do the same job with the build system or with the language of the project, without a new dependency.

**No global variable.** A setting that a global variable or a global command gives to every target moves to each target that needs it. The setting stays, only its place changes. The reference file names the global variables and the global commands of the build system, and what replaces each one. A build system without reference file: use its own way to give a setting to one target.

**Tests.** The build files register each test of the project: `enable_testing()` and `add_test` (CMake), `test()` (Meson), the script `test` (npm).

**A new build system.** Write the smallest build files: one target for each library and each program of the project, and one for each test.

## Step 3 — Check
1. Run the commands of `README.md` in the project, in their order. When a tool is not installed, the command is `not run`.
2. `git status --porcelain` must list no new and no changed file that the build wrote. If it lists one, complete `.gitignore`.
3. `git ls-files` must list no file of a build folder.

## Step 4 — Report
- The build system, and each file changed with the point that it fixes. When no file changed: say that the build system already meets the five points, and ask which other improvement the human partner wants.
- Each command with its local result: `passed`, `failed` or `not run`.
- The operating system where the commands were run. Each other operating system, by name: `not run`.
- Each build folder removed from git.
