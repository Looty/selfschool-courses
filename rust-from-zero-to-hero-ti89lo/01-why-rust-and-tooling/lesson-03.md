---
id: l03
title: "Lab 1: set up the tools and read three compiler errors"
quiz: quiz-03.yaml
resources: [../resources/lab1-toolchain/Cargo.toml, ../resources/lab1-toolchain/src/main.rs, ../resources/lab1-toolchain/broken/move_error.rs, ../resources/lab1-toolchain/broken/borrow_error.rs, ../resources/lab1-toolchain/broken/type_error.rs]
sources: [1, 2, 3, 7, 8, 20]
---
After this lab you will have built and run a Cargo project, linted and formatted it, and read the three compiler errors new Rust programmers meet most: a moved value, a conflicting borrow and a missing type.

This is a hands-on lab: do the steps on your own machine. The files were built and run with rustc 1.99.1 while writing this course.

## Shortcut: the ready-made files

Download the five files from this lesson's Resources and keep their folders: `Cargo.toml` and `src/main.rs` at the top, the three `*_error.rs` files in `broken/`. Then, inside that folder:

```bash
cargo run                                      # the fixed versions
cargo clippy                                   # no warnings expected
cargo fmt                                      # formats in place
rustc --edition 2024 broken/move_error.rs      # each of these fails on purpose
rustc --edition 2024 broken/borrow_error.rs
rustc --edition 2024 broken/type_error.rs
```

What you should see from `cargo run`:

```text
move:   hello, hello
borrow: [1, 2, 3, 10]
types:  43
```

The three `rustc` commands each stop with one error: `E0382`, `E0502` and `E0284`. Calling `rustc` directly on one file is fine for experiments; real projects use Cargo. [1]

## Step 1: error E0382, use of a moved value

```rust
let greeting = String::from("hello");
let moved = greeting;            // ownership moves to `moved`
println!("{moved}, {greeting}"); // error[E0382]: borrow of moved value
```

A `String` owns heap memory. Assigning it to another variable *moves* it: the old name becomes invalid, so the memory can never be freed twice. [3] The compiler suggests cloning; the fix in `main.rs` borrows instead (`let borrowed = &greeting;`), which reads the string without taking it. Chapter 3 explains both.

## Step 2: error E0502, a borrow conflict

```rust
let mut numbers = vec![1, 2, 3];
let first = &numbers[0];  // a shared borrow
numbers.push(10);         // error[E0502]: mutable borrow while `first` is used
println!("first = {first}");
```

`push` may reallocate the vector's buffer, which would leave `first` pointing at freed memory; Rust forbids changing data while a shared reference to it is still used. [3] [7] The fix copies the number out (`let first = numbers[0];`) so no reference is alive when `push` runs.

## Step 3: error E0284, type annotations needed

```rust
let n = "42".parse().unwrap(); // which type should `parse` produce?
```

`parse` can produce many types, and nothing here says which one. [2] The compiler's help text says to give `n` a type; the fix writes `let n: u32 = ...` and uses `expect` with a message instead of `unwrap`, which is the habit Chapter 5 recommends. [8]

## Check yourself

- Read the full text of each error, not just the first line. Every one points at two places: where the problem starts and where it bites.
- Add `let mut x = 42; println!("{x}");` and an unused `let y = 5;` to `main`, run `cargo build`, then `cargo fix --allow-dirty`. In our run it removed the needless `mut` and renamed `y` to `_y`, which silences the unused-variable warning. [20]
- Change `opt-level` for the dev profile in `Cargo.toml` and time `cargo build` before and after.

:::key-takeaways
- Rust's error messages name the rule, the two places involved and usually a fix.
- E0382 (moved value), E0502 (borrow conflict) and E0284 (type annotations needed) are the everyday ones.
- Run `cargo clippy` and `cargo fmt` as part of every change.
:::

:::glossary
- **Move**: transferring ownership of a value to another variable, leaving the old one unusable.
- **Clone**: making a full, independent copy of a value, including its heap data.
- **Shared borrow**: a read-only reference, written `&x`.
- **Mutable borrow**: a reference that allows changes, written `&mut x`.
- **Type annotation**: writing a type explicitly, as in `let n: u32`.
- **Reallocate**: move a growing buffer to a bigger block of memory.
:::
