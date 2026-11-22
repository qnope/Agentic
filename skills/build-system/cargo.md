# Cargo

Rules of the skill `build-system` for a project built with Cargo.

## No global variable
- Never set the variable `RUSTFLAGS`, and never write `rustflags` in `.cargo/config.toml`: they act on every crate, the dependencies too.
- A lint goes to the package that needs it: the table `[lints]` of its `Cargo.toml`.
