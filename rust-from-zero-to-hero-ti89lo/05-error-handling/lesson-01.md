---
id: l12
title: panic!, Result and the ? operator
quiz: quiz-12.yaml
sources: [8, 11, 33, 34]
---
After this lesson you can decide between panicking and returning an error, propagate errors with `?`, and give `main` a useful exit code.

## Two kinds of errors, no exceptions

Rust has no exceptions. It splits failures into **unrecoverable** ones, which are bugs and use `panic!`, and **recoverable** ones, such as a missing file, which are returned as a `Result<T, E>` value. [8]

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

## panic!

A panic prints a message and, by default, **unwinds**: it walks back up the stack running destructors, then ends the thread. [8] Setting `panic = "abort"` in a profile ends the process immediately instead, leaving cleanup to the operating system. [8] Setting the environment variable `RUST_BACKTRACE=1` prints the chain of calls that led to the panic; read it from the top until you reach a file you wrote. [8]

Indexing a `Vec` out of bounds panics. The Book contrasts this with C, where reading past the end of an array is undefined behavior and a known source of security holes (a buffer overread). [8]

## Result and match

```rust
use std::fs::File;
use std::io::ErrorKind;

let f = match File::open("hello.txt") {
    Ok(file) => file,
    Err(e) if e.kind() == ErrorKind::NotFound => File::create("hello.txt").expect("create file"),
    Err(e) => panic!("cannot open hello.txt: {e:?}"),
};
```

`File::open` returns `Result<File, io::Error>`, and `io::Error::kind()` tells you which kind of failure happened. [8] `Result` is marked `#[must_use]`, so ignoring one produces a compiler warning. [34]

## unwrap and expect

`unwrap()` returns the `Ok` value or panics; `expect("...")` does the same with your message. The Book notes that in production code most Rust programmers prefer `expect` with a message saying why the operation should succeed. [8] Both are fine in examples, prototypes and tests, where a panic is the desired outcome. [8]

## Propagating with ?

```rust
use std::fs;
use std::io;

fn read_username() -> Result<String, io::Error> {
    let name = fs::read_to_string("username.txt")?;
    Ok(name.trim().to_string())
}
```

`?` after a `Result` returns the `Ok` value, or returns early from the function with the `Err`. [8] Unlike a hand-written `match`, the error goes through `From::from`, so it is converted into the function's own error type; this is how one function can return a single error type for several kinds of failure. [8] `?` also works on `Option` inside functions that return `Option`, returning `None` early. [8] [33] It will not mix the two: use `ok_or(...)` to turn an `Option` into a `Result`, or `.ok()` for the reverse. [8]

## main can return Result

```rust
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    let text = std::fs::read_to_string("config.toml")?;
    println!("{} bytes", text.len());
    Ok(())
}
```

When `main` returns `Err`, the program exits with a nonzero status, following the C convention. [8] `Box<dyn Error>` means "any error type"; it is a *trait object*, which Chapter 6 explains. [8] Print user-facing errors to standard error with `eprintln!`, so they do not mix with normal output redirected to a file. [11]

## When to panic

Return `Result` by default: it lets the caller decide whether the failure is fatal. [8] Panic when continuing would be wrong: a broken invariant or contract, a situation that should be impossible, or a caller bug. [8] Use the type system to make bad input impossible: a type such as `Guess` whose constructor checks `1..=100` and whose field is private guarantees every `Guess` is valid, so no other function has to re-check. [8]

:::key-takeaways
- `panic!` is for bugs; `Result<T, E>` is for failures the caller can handle.
- `?` returns early with the error and converts it with `From`; it works on `Option` too.
- Prefer `expect` with a reason over `unwrap`; let `main` return `Result` for a correct exit code.
:::

:::glossary
- **Panic**: stopping because of a bug, with an error message.
- **Unwinding**: walking back up the call stack after a panic, running destructors.
- **Backtrace**: the list of function calls active when a panic happened.
- **Result**: the enum that is either `Ok(value)` or `Err(error)`.
- **Propagate**: pass an error back to the caller instead of handling it.
- **? operator**: return the error early, otherwise continue with the value.
- **must_use**: an attribute that makes the compiler warn if a value is ignored.
- **Invariant**: a condition that must always be true for a value to be valid.
- **Exit code**: the number a program returns to the shell; 0 means success.
- **Standard error / stderr**: the output stream meant for error messages.
:::
