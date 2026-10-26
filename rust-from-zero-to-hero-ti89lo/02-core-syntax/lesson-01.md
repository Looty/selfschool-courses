---
id: l04
title: Variables, types and integer overflow
quiz: quiz-04.yaml
sources: [2, 24, 45, 74]
---
After this lesson you can declare variables and constants, pick the right numeric type, and say exactly what happens when an integer overflows in debug and release builds.

## Immutable by default

```rust
let x = 5;        // immutable
// x = 6;         // error: cannot assign twice to immutable variable
let mut y = 5;    // mutable
y += 1;
const MAX_POINTS: u32 = 100_000; // always immutable, type required
```

Variables are immutable unless you write `mut`. [2] This is the opposite of C and C++, where you add `const` to forbid changes. A `const` must have its type written out, may only be set to a value the compiler can compute, and is named in `UPPER_SNAKE_CASE`. [2]

## Shadowing

You can declare a new variable with the same name, which *shadows* the old one: [2]

```rust
let spaces = "   ";        // &str
let spaces = spaces.len(); // usize: a new variable, a new type
```

Shadowing is not mutation: each `let` creates a fresh binding, so the type may change, and the final value can still be immutable. [2]

## Scalar types

| Kind | Types | Default |
|---|---|---|
| Signed integers | `i8 i16 i32 i64 i128 isize` | `i32` |
| Unsigned integers | `u8 u16 u32 u64 u128 usize` | |
| Floats | `f32 f64` (IEEE 754) | `f64` |
| Boolean | `bool` | |
| Character | `char`, 4 bytes, one Unicode scalar value | |

Integer sizes are fixed except `isize`/`usize`, which match the pointer width; you use `usize` to index collections. [2] Literals can carry a suffix and underscores: `57u8`, `1_000`, `0xff`, `0b1111_0000`, `b'A'`. [2] Unlike C, there are no implicit numeric conversions and no "truthy" integers: an `if` condition must be a `bool`. [2]

Tuples `(i32, f64, u8)` and fixed-size arrays `[i32; 5]` are the built-in compound types; the empty tuple `()` is called **unit** and is what a function "returns" when it returns nothing. [2] Indexing an array past its end panics at run time ("index out of bounds") instead of reading other memory. [2]

## Integer overflow, precisely

If a `u8` holding 255 is incremented: [2]

- **Debug builds** check and **panic**.
- **Release builds** (with `--release`) do not check; the value **wraps** around using two's complement, so 255 + 1 becomes 0.

This follows from the profiles: `dev` has `overflow-checks = true`, `release` has `overflow-checks = false`. [45] The Reference is explicit that overflow is still a programmer error even when it wraps, but it is never undefined behavior: implementations must give a well-defined two's-complement result. [24] The Book adds that relying on wrapping is considered an error. [2]

When overflow is possible, say what you want with an explicit method family: [2]

```rust
let x: u8 = 250;
x.checked_add(10)     // None: overflow is reported as None
x.wrapping_add(10)    // 4: wraps on purpose, in every build
x.overflowing_add(10) // (4, true): value plus an overflow flag
x.saturating_add(10)  // 255: clamps at the maximum
```

Those four results were checked on rustc 1.99.1. [74]

:::key-takeaways
- `let` is immutable; `let mut` allows change; `const` is a compile-time constant with a written type.
- Shadowing makes a new variable and may change the type.
- Overflow panics in debug and wraps in release; use `checked_`, `wrapping_`, `overflowing_` or `saturating_` to choose.
:::

:::glossary
- **Shadowing**: declaring a new variable with an existing name, hiding the old one.
- **Scalar**: a type holding a single value, such as a number or a bool.
- **usize / isize**: integer types as wide as a pointer on the target machine.
- **Two's complement**: the usual binary encoding of signed integers; wrapping follows it.
- **Overflow**: a result too big or too small for the integer type.
- **Panic**: Rust stopping the current thread with an error message because something went wrong.
- **Unit**: the empty tuple `()`, Rust's "no meaningful value".
- **Literal suffix**: a type tag on a number, like `u8` in `57u8`.
:::
