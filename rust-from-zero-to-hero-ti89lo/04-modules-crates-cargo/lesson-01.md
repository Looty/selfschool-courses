---
id: l10
title: Packages, crates and modules
quiz: quiz-10.yaml
sources: [6, 10, 13]
---
After this lesson you can lay out a Rust project with a library and a binary, split code into modules and files, and control what is public.

## Packages and crates

A **crate** is the smallest unit the compiler builds at once: either a **binary crate** (has `main`, produces an executable) or a **library crate** (no `main`, meant to be used by other code). [6] A **package** is one `Cargo.toml` plus the crates it builds: any number of binaries but at most one library. [6] Cargo finds them by convention: [6]

```text
my-tool/
├── Cargo.toml
└── src/
    ├── lib.rs        # library crate root (optional)
    ├── main.rs       # binary crate root named like the package
    └── bin/
        └── extra.rs  # another binary crate
```

A common layout keeps almost all logic in `lib.rs` and only a thin `main.rs` that calls it. The binary then uses the library like any other user would, and the library can be tested through its public API. [6] [10]

## Modules

Inside a crate, code is organized in a tree of **modules**, rooted at the crate root module named `crate`. [6]

```rust
// src/lib.rs
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

pub fn eat_at_restaurant() {
    crate::front_of_house::hosting::add_to_waitlist(); // absolute path
    front_of_house::hosting::add_to_waitlist();        // relative path
}
```

Paths start from `crate` (absolute), from the current module, from `self`, or from `super` (the parent module). [6]

### Modules in files

`mod garden;` in the crate root tells the compiler to load the module from `src/garden.rs` (or the older `src/garden/mod.rs`). A submodule `mod vegetables;` inside `garden.rs` is loaded from `src/garden/vegetables.rs`. [6] You declare each file once with `mod`; this is not a textual `#include`, and other files refer to its items by path. [6]

## Privacy

Everything is **private to its parent module by default**: functions, structs, enums, modules and constants. [6] Child modules can see their ancestors' items, but parents cannot see into children unless the item is `pub`. [6]

- `pub mod` makes the module visible but not its contents; each item needs its own `pub`. [6]
- A `pub struct` keeps its fields private unless each field is marked `pub`. A struct with private fields therefore needs a public constructor. [6]
- A `pub enum` makes all its variants public. [6]

Private-by-default is what lets you change internals without breaking users. [6]

## use, as and re-exports

`use` creates a shortcut for a path within the current scope only. [6]

```rust
use std::collections::HashMap;        // types: import the item itself
use std::fmt::Result;
use std::io::Result as IoResult;      // rename to avoid a clash
use std::io::{self, Write};           // nested import of io and io::Write

mod front_of_house { pub mod hosting { pub fn add_to_waitlist() {} } }
pub use crate::front_of_house::hosting; // re-export
```

By convention you import the parent module of a function (`hosting::add_to_waitlist()`) so it is clear the function is not local, but import structs and enums by their full path. [6] `pub use` **re-exports** an item, so outside code can write `my_crate::hosting` even though it lives deeper inside. [6] Re-exporting lets a crate offer a simple public structure that differs from its internal one. [13] Glob imports (`use std::collections::*;`) are mostly used in test modules, because they hide where names come from. [6]

:::key-takeaways
- A package has at most one library crate and any number of binaries; keep logic in `lib.rs`.
- `mod name;` loads `name.rs`; everything is private until marked `pub`, field by field for structs.
- `use` shortens paths in one scope; `pub use` re-exports to shape your public API.
:::

:::glossary
- **Crate**: one library or executable that the compiler builds as a unit.
- **Package**: a Cargo.toml and the crates it builds.
- **Crate root**: the file the compiler starts from, usually `src/lib.rs` or `src/main.rs`.
- **Module**: a named namespace inside a crate that groups items and controls privacy.
- **Path**: the name of an item through the module tree, like `crate::a::b`.
- **pub**: the keyword that makes an item visible outside its module.
- **Re-export**: making an item available under a new path with `pub use`.
- **Glob import**: `use path::*`, bringing every public item into scope.
:::
