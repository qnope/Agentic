# Meson

Rules of the skill `build-system` for a project built with Meson.

## No global variable
- Never call `add_global_arguments`, `add_global_link_arguments`, `add_project_arguments` or `add_project_link_arguments`: they act on every target. Give the setting to the target that needs it, with its arguments `cpp_args:`, `link_args:`, `include_directories:` and `dependencies:`.
- The `default_options` of `project()` (`cpp_std`, `warning_level`) are not global variables: they are the way Meson declares the version of the language and the warnings. They stay.
