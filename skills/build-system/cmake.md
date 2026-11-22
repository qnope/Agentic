# CMake

Rules of the skill `build-system` for a project built with CMake.

## Commands
- Windows chooses the build type when it builds, and `ctest` runs no test without it. So the build command has `--config Debug` and the test command has `-C Debug`.
- `Debug` keeps the `assert` of the tests: never make `Release` the default build type.

## No global variable: always a target
Never write `set(CMAKE_<NAME> ...)`, and never call a command that acts on every target. Give each setting to the target that needs it:

| Never | Always |
|---|---|
| `set(CMAKE_CXX_STANDARD 17)`, the option `-std=c++17` | `target_compile_features(<target> PUBLIC cxx_std_17)` |
| `set(CMAKE_CXX_FLAGS ...)`, `add_compile_options(...)` | `target_compile_options(<target> PRIVATE ...)` |
| `include_directories(...)` | `target_include_directories(<target> PUBLIC ...)` |
| `add_definitions(...)`, `add_compile_definitions(...)` | `target_compile_definitions(<target> PRIVATE ...)` |
| `link_libraries(...)`, `link_directories(...)` | `target_link_libraries(<target> PRIVATE <library>)` |
| `set(CMAKE_CXX_COMPILER ...)`, `set(CMAKE_BUILD_TYPE ...)` | nothing: the person who builds chooses them on the command line |
| another `set(CMAKE_<NAME> ...)` | the property `<NAME>` of the target: `set_target_properties(<target> PROPERTIES <NAME> ...)` |

- `PUBLIC`: the targets that link this target get the setting too (the include folder and the version of the language of a library). `PRIVATE`: this target only.
- A target that links a library gets the `PUBLIC` settings of the library: do not write them again.
- A compiler option goes only to the compilers that know it. The existing options stay, on each target that had them:

```
if(MSVC)
  target_compile_options(<target> PRIVATE /W4)
else()
  target_compile_options(<target> PRIVATE -Wall -Wextra)
endif()
```

- A `CMAKE_` variable that no target property replaces (`CMAKE_MODULE_PATH`) stays. Name it in the report.
