---
id: l23
title: Unit, integration and doc tests
quiz: quiz-23.yaml
sources: [10, 13]
---
After this lesson you can write and run unit tests, integration tests and documentation tests, check for panics and errors, and control which tests run and how.

## A test is a function with #[test]

```rust
pub fn add_two(a: u64) -> u64 { a + 2 }

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds_two() {
        assert_eq!(add_two(2), 4);
    }

    #[test]
    fn not_zero() {
        assert_ne!(add_two(0), 0, "add_two(0) should never be zero");
    }
}
```

`cargo test` builds a test runner that calls every `#[test]` function; a test fails when it panics. [10] `assert!` checks a bool; `assert_eq!` and `assert_ne!` compare two values and print both when they fail, which requires the values to implement `PartialEq` and `Debug` (usually via `#[derive(PartialEq, Debug)]`). [10] Rust calls the arguments `left` and `right`, and their order does not matter. [10] Extra arguments after the required ones form a custom failure message, as with `format!`. [10]

`#[cfg(test)]` compiles the module only for `cargo test`, so tests add nothing to normal builds. [10] Because the test module is a child module, `use super::*` brings in the code under test, private functions included; Rust lets you test private functions. [10]

## Expecting a panic, or returning a Result

```rust
#[test]
#[should_panic(expected = "less than or equal to 100")]
fn rejects_large_guess() {
    Guess::new(200);
}

#[test]
fn parses() -> Result<(), String> {
    let n: i32 = "42".parse().map_err(|e| format!("{e}"))?;
    if n == 42 { Ok(()) } else { Err(format!("got {n}")) }
}
```

`should_panic` passes only if the body panics; with `expected`, the panic message must contain that text, which keeps the test from passing for the wrong reason. [10] A test may instead return `Result<(), E>` and use `?`; such tests cannot use `should_panic`, and to assert an error you check `value.is_err()`. [10]

## Running tests

| Command | Effect |
|---|---|
| `cargo test` | all tests, in parallel threads |
| `cargo test add` | only tests whose name contains `add` |
| `cargo test -- --test-threads=1` | one at a time |
| `cargo test -- --show-output` | also show `println!` output of passing tests |
| `cargo test -- --ignored` | only tests marked `#[ignore]` |
| `cargo test -- --include-ignored` | everything |

Arguments before `--` go to Cargo, arguments after it go to the test binary. [10] Because tests run in parallel by default, they must not depend on each other or on shared state such as one file or the current directory. [10] Output from passing tests is captured unless you ask for it. [10] Mark slow tests `#[ignore]` and run them on purpose. [10]

## Integration tests

Files in a top-level `tests/` directory are **integration tests**. Each file is compiled as a separate crate that can only use your library's public API, exactly like an outside user. [10]

```text
adder/
├── src/lib.rs
└── tests/
    ├── common/mod.rs      # shared helpers, not a test crate itself
    └── integration_test.rs
```

```rust
// tests/integration_test.rs
use adder::add_two;
mod common;

#[test]
fn it_adds_two() {
    common::setup();
    assert_eq!(add_two(2), 4);
}
```

Shared helpers go in `tests/common/mod.rs` rather than `tests/common.rs`, so Cargo does not treat them as one more test file. [10] Run one file with `cargo test --test integration_test`. [10] A binary-only crate (just `main.rs`) cannot be imported by integration tests, one more reason to keep the logic in `lib.rs`. [10]

## Documentation tests

Code blocks in `///` doc comments are compiled and run by `cargo test` under the "Doc-tests" heading, so examples in your documentation cannot silently go stale. [13] The next lesson covers writing those comments.

:::key-takeaways
- Unit tests live in a `#[cfg(test)] mod tests` beside the code and may test private items.
- Integration tests in `tests/` see only the public API; each file is its own crate.
- Tests run in parallel: keep them independent; use filters, `#[ignore]` and `--` flags to control runs.
:::

:::glossary
- **Unit test**: a focused test of one piece of code, placed next to it.
- **Integration test**: a test in `tests/` that uses the crate only through its public API.
- **Doc test**: a code example in documentation that `cargo test` compiles and runs.
- **#[cfg(test)]**: compile this item only when building tests.
- **assert_eq!**: a macro that panics, showing both values, if two values differ.
- **should_panic**: an attribute for tests that pass only if the code panics.
- **Test runner**: the program cargo builds to find, run and report tests.
- **Captured output**: printed text that the runner hides unless a test fails.
:::
