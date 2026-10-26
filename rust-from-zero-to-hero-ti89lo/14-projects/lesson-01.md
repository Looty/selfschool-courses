---
id: l35
title: "Lab 4: a command-line task tracker"
quiz: quiz-35.yaml
resources: [../resources/lab4-tasks/Cargo.toml, ../resources/lab4-tasks/Cargo.lock, ../resources/lab4-tasks/src/lib.rs, ../resources/lab4-tasks/src/main.rs, ../resources/lab4-tasks/tests/store.rs]
sources: [10, 42, 53, 54, 56, 57]
---
After this lab you will have a working CLI that adds, completes, removes and lists tasks stored as JSON, built from clap, serde, thiserror and anyhow, with integration tests for its library.

This is a hands-on lab. The first build downloads crates from crates.io, so it needs internet access once. It was built, tested and run with rustc 1.99.1, clap 4.6.7, serde 1.0.229, serde_json 1.0.154, thiserror 2.0.21 and anyhow 1.0.104.

## Shortcut: the ready-made files

Download the five files into `tasks/`, keeping `src/` and `tests/`. Then:

```bash
cargo test                          # 4 integration tests
cargo run -- add "Read chapter 3"
cargo run -- add "Do lab 4"
cargo run -- done 1
cargo run -- list --all
cargo run -- done 9                 # an error, exit status 1
cargo run -- --help
```

What you should see from `list --all` and `done 9`:

```text
[x] #1 Read chapter 3
[ ] #2 Do lab 4
Error: no task with id 9
```

`cargo test` prints `4 passed; 0 failed` for `tests/store.rs`. The tasks are saved in `tasks.json` in the current folder (choose another file with `-f`). The shipped `Cargo.lock` pins the exact versions that were tested; keep it. [42]

## Step 1: the library (src/lib.rs)

`Store` holds a `next_id` and a `Vec<Task>` and derives `Serialize` and `Deserialize`, which need serde's `derive` feature. [53] `load` treats a missing file as an empty store by matching on `io::ErrorKind::NotFound`, and lets every other error propagate with `?`. Methods return `Result<_, StoreError>` and nothing in the library prints or exits, so it is easy to test.

## Step 2: typed errors with thiserror

```rust
#[derive(Debug, Error)]
pub enum StoreError {
    #[error("could not read or write the task file")]
    Io(#[from] io::Error),
    #[error("the task file is not valid JSON")]
    Json(#[from] serde_json::Error),
    #[error("no task with id {0}")]
    NotFound(u32),
    #[error("a task title cannot be empty")]
    EmptyTitle,
}
```

`#[from]` generates the `From` conversions that let `?` turn I/O and JSON errors into `StoreError`, and makes them the `source()`. [56] Callers can `match` on `NotFound` and `EmptyTitle`; the tests do exactly that with `matches!`.

## Step 3: the binary with clap and anyhow (src/main.rs)

```rust
#[derive(Parser)]
#[command(version, about)]
struct Cli {
    /// Where the tasks are stored
    #[arg(short, long, default_value = "tasks.json")]
    file: PathBuf,
    #[command(subcommand)]
    command: Command,
}
```

`#[derive(Parser)]` builds the argument parser from the struct; `#[command(version, about)]` reads the version and description from `Cargo.toml`, and doc comments become help text. [54] Subcommands are an enum with `#[derive(Subcommand)]`. [54] `main` returns `anyhow::Result<()>` and adds context such as `failed to load tasks.json` with `.with_context(...)`; a `StoreError` passes through `?` unchanged and is printed as `Error: no task with id 9`. [57]

## Step 4: integration tests (tests/store.rs)

The tests use only the public API (`use tasks::{Store, StoreError};`), as integration tests must. [10] Each test uses its own file in the system temp directory so the tests can run in parallel without interfering. [10]

## Check yourself

- Add an `edit <id> <title>` subcommand. Which file gets the logic, which the parsing, and what new test do you add?
- Write `not json` into `tasks.json` and run `cargo run -- list`. Which context and cause are printed?
- Run `cargo run -- add "   "`. Where does the message come from?

:::key-takeaways
- Library: domain logic plus a thiserror enum; binary: clap parsing plus anyhow context.
- `#[derive(Parser, Subcommand)]` turns structs and enums into a full CLI with help and version.
- Integration tests exercise the public API; give each test its own files.
:::

:::glossary
- **CLI**: a command-line interface, a program driven by typed commands and flags.
- **Subcommand**: a verb after the program name, such as `add` in `tasks add`.
- **Serialize / Deserialize**: converting a value to and from a format such as JSON.
- **JSON**: a common text format for structured data.
- **Context (anyhow)**: a message added to an error describing what the program was doing.
- **matches!**: a macro that returns whether a value matches a pattern.
- **Temp directory**: a system folder for short-lived files.
:::
