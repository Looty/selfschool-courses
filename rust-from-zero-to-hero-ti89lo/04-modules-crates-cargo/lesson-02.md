---
id: l11
title: Dependencies, Cargo.lock, features and workspaces
quiz: quiz-11.yaml
sources: [8, 13, 42, 43, 44, 45, 46, 53, 54]
---
After this lesson you can add dependencies with the right version requirement, explain what Cargo.lock is for, turn crate features on and off, and organize several packages as a workspace.

## Version requirements

```toml
[dependencies]
serde = { version = "1.0.229", features = ["derive"] }
rand = "0.10.1"
```

A plain version string is a **caret requirement**: it means "this version or any later SemVer-compatible one". [43] Compatibility is decided by the left-most non-zero number: [43]

| Requirement | Allows |
|---|---|
| `"1.2.3"` (same as `"^1.2.3"`) | `>=1.2.3, <2.0.0` |
| `"0.2.3"` | `>=0.2.3, <0.3.0` |
| `"0.0.3"` | `>=0.0.3, <0.0.4` |
| `"~1.2.3"` (tilde) | `>=1.2.3, <1.3.0` |
| `"=1.2.3"` | exactly 1.2.3 |

So for `0.x` crates a minor bump counts as breaking. Pre-release versions such as `1.0.0-alpha` are never picked unless you ask for one. [43] The Cargo Book recommends the default operator and warns against upper limits below the next incompatible version, because they can make the dependency graph impossible to resolve. [43]

`cargo add serde --features derive` edits `Cargo.toml` for you. [54]

## Cargo.toml vs Cargo.lock

`Cargo.toml` is written by you and describes dependencies broadly; `Cargo.lock` is written by Cargo, records the exact version (and Git commit) of every dependency, and should not be edited by hand. [42] Its job is reproducible builds: someone building your project tomorrow gets the same versions you tested today. [42] The Cargo Book's advice: "When in doubt, check Cargo.lock into the version control system". [42] To move to newer compatible versions on purpose, run `cargo update` (all dependencies) or `cargo update regex` (one). [42]

## Features

Crates can define optional pieces in a `[features]` table; all features are off unless enabled. [44] A `default` feature lists what is on unless the user opts out with `--no-default-features` or `default-features = false`. [44]

```toml
[features]
default = ["json"]
json = ["dep:serde_json"]     # enabling `json` turns on an optional dependency

[dependencies]
serde_json = { version = "1.0.154", optional = true }
```

Code tests for a feature with `#[cfg(feature = "json")]`. [44] The `dep:` prefix (Rust 1.60 and later) keeps the optional dependency from also becoming a feature of its own name. [44] Serde's derive macros, for example, live behind its `derive` feature. [53] If the compiler says a trait is "not implemented" even though you derived it, you probably have two incompatible versions of the same crate; `cargo tree -d` shows duplicates. [53]

## Profiles

You saw `dev` and `release` in Chapter 1. You override any default setting in `Cargo.toml`; anything you do not set keeps its default. [45] [13] For example, the Book shows switching panics from unwinding to aborting in release builds, to make the binary smaller (Chapter 5 explains unwinding): [8]

```toml
[profile.release]
panic = "abort"

[profile.dev]
opt-level = 1     # a little optimization in debug builds
```

`cargo test` uses the `test` profile, which inherits from `dev`; `cargo bench` uses `bench`, which inherits from `release`. [45]

## Workspaces

A **workspace** is a set of packages built together. They share one `Cargo.lock` and one `target/` directory, so every member uses the same dependency versions and nothing is compiled twice. [46] [13]

```toml
# Cargo.toml at the repository root: a "virtual manifest" with no [package]
[workspace]
members = ["crates/*"]
resolver = "3"
```

A virtual manifest must set `resolver` because it has no package edition to infer it from. [46] Commands like `cargo test` at the root run for every member, and `-p name` picks one. [13] `[profile.*]` sections only take effect in the workspace root. [46]

## Publishing, briefly

`cargo publish` uploads a version to crates.io permanently; a version can never be overwritten or deleted, only **yanked**, which stops new projects from picking it while existing Cargo.lock files keep working. [13] A yank does not remove leaked secrets. [13]

:::key-takeaways
- `"1.2.3"` means `^1.2.3`: any compatible version; for `0.x`, the minor number is the breaking one.
- Commit Cargo.lock; update deliberately with `cargo update`.
- Features are opt-in switches; workspaces share one lockfile and one target directory.
:::

:::glossary
- **Dependency**: another crate your package uses.
- **SemVer**: semantic versioning, MAJOR.MINOR.PATCH, where a major bump signals breaking changes.
- **Caret requirement**: the default version rule that accepts compatible updates.
- **Lockfile**: a file pinning the exact versions used in a build.
- **Feature**: a named, optional part of a crate that can be switched on.
- **Workspace**: several packages managed together with one lockfile.
- **Virtual manifest**: a workspace Cargo.toml with no package of its own.
- **Yank**: marking a published version so new projects will not use it.
- **opt-level**: how hard the compiler optimizes, from 0 (none) to 3.
:::
