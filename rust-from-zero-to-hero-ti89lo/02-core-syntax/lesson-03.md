---
id: l06
title: Structs, enums, Option and match
quiz: quiz-06.yaml
sources: [4, 5, 33, 74]
---
After this lesson you can model data with structs and enums, attach methods to them, replace null pointers with `Option`, and handle every case with an exhaustive `match`.

## Structs and methods

```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn square(size: u32) -> Self {            // associated function, no self
        Self { width: size, height: size }
    }
    fn area(&self) -> u32 {                   // method that reads
        self.width * self.height
    }
    fn grow(&mut self, by: u32) {             // method that writes
        self.width += by;
    }
}

let mut r = Rectangle::square(3);
r.grow(2);
println!("{r:?} has area {}", r.area());     // Rectangle { width: 5, height: 3 } has area 15
```

Methods live in an `impl` block, and their first parameter says how they use the instance: `&self` borrows it to read, `&mut self` borrows it to change, and plain `self` consumes it. [4] `&self` is short for `self: &Self`, where `Self` is the type the block is for. [4] Functions in the block without `self` are **associated functions**, called with `::`; constructors are often named `new`, but the name has no special meaning. [4]

There is no `->` operator. When you call `r.area()`, Rust automatically adds the `&`, `&mut` or `*` needed to match the method's receiver. [4] `#[derive(Debug)]` asks the compiler to generate debug printing, used by `{:?}` and `{:#?}`. [4] The `dbg!` macro prints a value with file and line to stderr and returns it. [4]

Tuple structs such as `struct Meters(f64);` give a distinct type to one or more unnamed fields: a `Meters` cannot be passed where another tuple struct with the same fields is expected. [4] Unit-like structs (`struct Marker;`) hold no data. [4]

## Enums carry data

A Rust enum is a tagged union: each variant may hold different data. [5]

```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}
```

Each variant name also works as a constructor, as in `Message::Write(String::from("hi"))`. [5]

## Option instead of null

Rust has no null. A value that may be missing has type `Option<T>`, defined as `enum Option<T> { None, Some(T) }` and always in scope. [5] Because `Option<i32>` and `i32` are different types, the compiler will not let you use a maybe-missing value as if it were present; you must handle `None` first. [5] The Book quotes Tony Hoare calling null references his "billion-dollar mistake". [5]

This costs nothing for pointers: Rust guarantees that `Option<Box<T>>`, `Option<&T>` and similar types are the same size as the pointer itself, with `None` stored as the null bit pattern. [33] On a 64-bit target both `Box<i32>` and `Option<Box<i32>>` measured 8 bytes. [74]

## match is exhaustive

```rust
fn describe(m: &Message) -> String {
    match m {
        Message::Quit => "quit".to_string(),
        Message::Move { x, y } => format!("move to {x},{y}"),
        Message::Write(text) => format!("write {text}"),
        Message::ChangeColor(r, g, b) => format!("color {r} {g} {b}"),
    }
}
```

A `match` must cover every possible value or it does not compile, and the error lists the missing patterns. [5] `_` matches anything without binding it; a named catch-all like `other` binds the value. [5]

For one interesting case, `if let` is shorter but drops the exhaustiveness check; `let ... else` binds on success and requires the `else` branch to leave the function: [5]

```rust
if let Some(n) = maybe_number { println!("{n}"); }

let Some(n) = maybe_number else { return; };
// n is usable here
```

:::key-takeaways
- `impl` blocks hold methods (`&self`, `&mut self`, `self`) and associated functions (`Type::new`).
- Enums carry per-variant data; `Option<T>` replaces null at no space cost for pointers.
- `match` must be exhaustive; use `if let` or `let ... else` for the single-case shortcuts.
:::

:::glossary
- **Struct**: a type that groups named fields.
- **impl block**: where methods and associated functions of a type are defined.
- **Method**: a function whose first parameter is the instance (`self`).
- **Associated function**: a function in an `impl` block without `self`, called as `Type::name`.
- **Receiver**: the `self` parameter that says how a method uses the instance.
- **Enum**: a type whose value is exactly one of several variants, each with its own data.
- **Tagged union**: a value that stores which variant it is plus that variant's data.
- **Option**: the standard enum for "a value or nothing".
- **Exhaustive**: covering every possible case.
- **derive**: an attribute asking the compiler to generate a trait implementation.
:::
