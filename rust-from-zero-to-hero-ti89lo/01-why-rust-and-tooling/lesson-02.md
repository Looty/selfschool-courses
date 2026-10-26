---
id: l02
title: "The toolchain: rustup, cargo and friends"
quiz: quiz-02.yaml
sources: [1, 13, 20, 45, 64, 67, 71]
---
After this lesson you can install Rust, create and build a project with Cargo, and use the formatter, linter and editor support that ship with it.

## rustup: the toolchain manager

The usual way to install Rust is **rustup**, a command-line tool that installs and updates Rust versions and their tools. [1] On Linux and macOS you run the install script from the Book; on Windows you use the installer from rust-lang.org, which also asks for the Visual Studio build tools because Rust needs a linker. [1]

```bash
rustc --version      # e.g. rustc 1.99.1 (58cf8f9c3 2026-10-13)
rustup update        # move to the newest stable release
rustup doc           # open the documentation installed on your machine
```

Rust is published on three **channels**: stable every six weeks, beta (the next stable), and nightly, built every night. [71] Some tools in this course, such as Miri, need nightly; you can install it next to stable with `rustup toolchain install nightly` without changing your default. [71]

## Cargo: build tool and package manager

`cargo new hello` creates a folder with `Cargo.toml` and `src/main.rs`, and starts a Git repository. [1] The generated manifest names the package and sets the edition:

```toml
[package]
name = "hello"
version = "0.1.0"
edition = "2024"

[dependencies]
```

The commands you will use every day: [1]

| Command | What it does |
|---|---|
| `cargo check` | type-checks without producing a binary; the fastest feedback |
| `cargo build` | builds a debug binary in `target/debug/` |
| `cargo run` | builds if needed, then runs |
| `cargo build --release` | optimized build in `target/release/` |
| `cargo test` | builds and runs the tests (chapter 9) |

The first build also writes `Cargo.lock`, which records the exact version of every dependency. [1] Chapter 4 explains why you commit it.

Debug and release builds use different **profiles**. By default `dev` uses `opt-level = 0` and keeps debug assertions and overflow checks on; `release` uses `opt-level = 3` and turns overflow checks off. [45] Always benchmark with `--release`. [1]

## Formatter, fixer and linter

Three tools come with a standard installation: [20]

- `cargo fmt` runs **rustfmt**, which formats code in the community style so nobody argues about layout.
- `cargo fix` applies the compiler's own suggested fixes, such as removing an unneeded `mut`; it also migrates code between editions.
- `cargo clippy` runs **Clippy**, which has over 800 extra lints. [67]

Clippy groups its lints into categories. `correctness` (code that is outright wrong) is an error by default; `suspicious`, `style`, `complexity` and `perf` warn; `pedantic`, `restriction`, `nursery` and `cargo` are off until you enable them. [67] Its docs warn that `restriction` should never be enabled as a whole. [67] `cargo clippy --fix` applies the suggestions it can apply automatically.

## Editor support

The Rust project recommends **rust-analyzer**, a language server that gives any supporting editor completion, jump-to-definition and inline errors. [20] In VS Code it is an extension; most other editors support it too.

## Practice beyond this course

Rustlings is a set of small exercises from the Rust project, meant to be done alongside the Book: [64]

```bash
cargo install rustlings
rustlings init
cd rustlings/
rustlings
```

`cargo install` builds a program from crates.io and puts it in `~/.cargo/bin`, which must be on your `PATH`. [13]

:::key-takeaways
- `rustup` installs and updates Rust; `cargo` builds, runs, tests and manages dependencies.
- Use `cargo check` while editing, `cargo build --release` for real measurements.
- `cargo fmt`, `cargo clippy` and rust-analyzer come with Rust; use them from day one.
:::

:::glossary
- **rustup**: the installer and version manager for Rust.
- **Toolchain**: one installed version of the compiler and its tools.
- **Channel**: a release stream: stable, beta or nightly.
- **Nightly**: the build made every night, with unfinished features available.
- **Manifest / Cargo.toml**: the file that describes a package and its dependencies.
- **Cargo.lock**: the file Cargo writes with the exact dependency versions used.
- **Profile**: a named set of compiler settings, such as dev or release.
- **Linker**: the program that joins compiled pieces into one executable.
- **rustfmt**: the standard code formatter.
- **Clippy**: the standard extra linter.
- **Lint**: an automatic check that warns about suspicious or unidiomatic code.
- **rust-analyzer**: the language server that powers Rust support in editors.
:::
