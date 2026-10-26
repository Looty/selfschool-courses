---
id: l13
title: Error types, thiserror and anyhow
quiz: quiz-13.yaml
sources: [8, 39, 56, 57, 66]
---
After this lesson you can write your own error type that implements `std::error::Error`, generate one with thiserror, and use anyhow in applications to add context to errors.

## The Error trait

`std::error::Error` is the standard interface for error values. It requires `Debug` and `Display`, so every error can be printed for developers and for users. [39] The standard library's style for messages is concise lowercase sentences without trailing punctuation, such as `invalid digit found in string`. [39]

An error may report its cause with `source()`, which returns the lower-level error it wraps. A wrapping error should either return the inner error from `source()` or include it in its own `Display` text, but not both, so the message is not printed twice. [39]

```rust
use std::{error::Error, fmt, io};

#[derive(Debug)]
pub enum ConfigError {
    Io(io::Error),
    Missing(&'static str),
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ConfigError::Io(_) => write!(f, "could not read the config file"),
            ConfigError::Missing(key) => write!(f, "missing key `{key}`"),
        }
    }
}

impl Error for ConfigError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            ConfigError::Io(e) => Some(e),
            ConfigError::Missing(_) => None,
        }
    }
}

impl From<io::Error> for ConfigError {
    fn from(e: io::Error) -> Self { ConfigError::Io(e) }
}
```

The `From` implementation is what lets `?` turn an `io::Error` into a `ConfigError` automatically. [8] The Rust API Guidelines ask that error types be "meaningful and well-behaved". [66]

## thiserror: derive it

That is a lot of boilerplate. The **thiserror** crate generates the same code from attributes: [56]

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ConfigError {
    #[error("could not read the config file")]
    Io(#[from] std::io::Error),
    #[error("missing key `{0}`")]
    Missing(&'static str),
}
```

`#[error("...")]` writes `Display` (fields can be interpolated, `{0}` or `{name}`), and `#[from]` writes the `From` impl and marks the field as the `source()`. [56] thiserror "deliberately does not appear in your public API": the result is the same as a handwritten implementation, so switching either way is not a breaking change. [56] `#[error(transparent)]` forwards both `Display` and `source` to an inner error, useful for an opaque public error type whose representation can change. [56]

## anyhow: one error type for applications

In application code you often just want "any error, with a good message". **anyhow** provides `anyhow::Error`, a trait-object-based type, and `anyhow::Result<T>`; `?` converts any `std::error::Error` into it. [57] Its key feature is context: [57]

```rust
use anyhow::{Context, Result};

fn load(path: &str) -> Result<String> {
    std::fs::read_to_string(path)
        .with_context(|| format!("failed to read {path}"))
}
```

Printed from `main`, this shows the chain: your context first, then `Caused by:` and the underlying "No such file or directory" error. [57] `anyhow!("...")` builds a one-off error and `bail!("...")` returns one early. [57] You can still recover a specific type with `downcast_ref::<MyError>()`. [57]

## Which one when?

thiserror's own documentation points to anyhow for "application code", and anyhow suggests thiserror when you want to define your own error types. [56] [57] A common split, used in Lab 4 of this course:

- **Libraries**: a specific error enum (handwritten or with thiserror), so callers can `match` on the cases.
- **Binaries**: `anyhow::Result` in `main` and glue code, adding `.context(...)` at each layer.

:::key-takeaways
- An error type implements `Debug + Display + Error`; `source()` exposes the cause, `From` enables `?`.
- thiserror derives that boilerplate and leaves no trace in your public API.
- anyhow gives applications one error type plus `.context()`; libraries usually expose specific enums.
:::

:::glossary
- **Error trait**: the standard interface every error type implements.
- **Display**: the trait for user-facing text, used by `{}`.
- **Debug**: the trait for developer-facing text, used by `{:?}`.
- **source()**: the method that returns the error that caused this one.
- **From**: the conversion trait that `?` uses to change error types.
- **Boilerplate**: repetitive code that must be written but adds little.
- **Trait object**: a value of "some type implementing a trait", such as `Box<dyn Error>`; see Chapter 6.
- **Context**: extra text attached to an error saying what the program was doing.
- **Downcast**: getting the concrete type back from a "some error" value.
:::
