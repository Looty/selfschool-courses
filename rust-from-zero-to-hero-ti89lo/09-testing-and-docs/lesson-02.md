---
id: l24
title: Documentation, API guidelines and lints
quiz: quiz-24.yaml
sources: [13, 21, 66, 67]
---
After this lesson you can write doc comments that become HTML documentation and tests, follow the main Rust API Guidelines, and use lint levels to keep a code base clean.

## Doc comments

````rust
//! A tiny arithmetic crate. (`//!` documents the enclosing item: here, the crate.)

/// Adds one to the number given.
///
/// # Examples
///
/// ```
/// let answer = my_crate::add_one(5);
/// assert_eq!(6, answer);
/// ```
///
/// # Panics
///
/// Panics if `x` is `i32::MAX`, because the result would overflow.
pub fn add_one(x: i32) -> i32 {
    x.checked_add(1).expect("overflow in add_one")
}
````

`///` comments document the item that follows and support Markdown; `//!` documents the item that contains them, typically the crate in `src/lib.rs`. [13] `cargo doc` generates HTML in `target/doc`, and `cargo doc --open` also builds the docs of your dependencies and opens them in a browser. [13]

Common sections are **Examples**, **Panics** (when the function can panic), **Errors** (what kinds of `Err` it returns and when) and **Safety** (for `unsafe` functions: what the caller must guarantee). [13] Examples in doc comments run as tests with `cargo test`, so they fail as soon as they drift from the code. [13]

## Shape the public API with pub use

Users should not have to know your internal module tree. Re-export the important items at the crate root with `pub use self::kinds::PrimaryColor;` so they can write `use art::PrimaryColor;`, and `cargo doc` lists the re-exports on the front page. [13]

## The Rust API Guidelines

The Library team's API Guidelines are a checklist for public crates. A selection: [66]

| ID | Guideline |
|---|---|
| C-CONV | Conversions follow `as_`, `to_`, `into_` naming |
| C-ITER | Collections offer `iter`, `iter_mut`, `into_iter` |
| C-COMMON-TRAITS | Types eagerly implement `Clone`, `Debug`, `PartialEq`, `Default` and friends |
| C-GOOD-ERR | Error types are meaningful and well-behaved |
| C-SEND-SYNC | Types are `Send` and `Sync` where possible |
| C-EXAMPLE | All items have a rustdoc example |
| C-QUESTION-MARK | Examples use `?`, not `unwrap` |
| C-FAILURE | Docs include error, panic and safety considerations |
| C-NEWTYPE | Newtypes provide static distinctions |
| C-CUSTOM-TYPE | Arguments convey meaning through types, not `bool` or `Option` |
| C-STRUCT-PRIVATE | Structs have private fields |
| C-SEALED | Sealed traits protect against downstream implementations |

C-CUSTOM-TYPE in practice: `Widget::new(Size::Small, Shape::Round)` reads better and is harder to misuse than `Widget::new(true, false)`.

## Lint levels

Lints, from rustc or Clippy, have a level: allow, warn or deny. Clippy's groups come with defaults: `clippy::correctness` is deny; `suspicious`, `style`, `complexity` and `perf` warn; `pedantic`, `nursery`, `restriction` and `cargo` are allowed (off). [67] You can raise or lower levels in code:

```rust
#![warn(clippy::pedantic)]          // crate-wide: opt into strict lints
#[allow(clippy::too_many_arguments)] // one item: silence a lint you disagree with
fn build(/* ... */) {}
```

The Clippy docs warn that `restriction` "should, emphatically, not be enabled as a whole": pick individual lints from it. [67] Since Rust 1.97, Cargo's `build.warnings` setting controls how warnings from your own packages are treated, for example to keep CI builds warning-free, replacing the older `-Dwarnings` flag approach. [21]

:::low-confidence
The exact values accepted by `build.warnings` were not read in full for this course; check the Cargo configuration reference for your Cargo version before using it in CI. [21]
:::

:::key-takeaways
- `///` documents the next item, `//!` the enclosing one; examples in docs run as tests.
- Write Examples, Panics, Errors and Safety sections; re-export key items at the root.
- Follow the API Guidelines checklist; tune lint levels per crate or item, never enable `clippy::restriction` wholesale.
:::

:::glossary
- **Doc comment**: a `///` or `//!` comment that becomes generated documentation.
- **rustdoc**: the tool behind `cargo doc` that turns doc comments into HTML.
- **API**: the public functions and types other code uses.
- **Re-export**: making an item available at another path with `pub use`.
- **Lint level**: whether a lint is ignored (allow), reported (warn) or fails the build (deny).
- **Sealed trait**: a public trait that outside crates cannot implement.
- **CI (continuous integration)**: automated builds and tests run on every change.
:::
