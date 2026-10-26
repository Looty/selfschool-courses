---
id: l32
title: Patterns in depth, let chains and if-let guards
quiz: quiz-32.yaml
sources: [5, 18, 21, 22, 74]
---
After this lesson you can use every kind of pattern (literals, ranges, destructuring, `_`, `..`, guards, `@`), tell refutable from irrefutable patterns, and use the newer let chains and if-let guards.

## Patterns are everywhere

Patterns appear in `match` arms, `if let`, `while let`, `let`, `for` loops, and function and closure parameters. [18]

```rust
let (x, y, z) = (1, 2, 3);                          // let destructures
for (index, value) in ['a', 'b'].iter().enumerate() {}  // for destructures
fn print_point(&(x, y): &(i32, i32)) { println!("({x}, {y})"); } // parameters too

let mut stack = vec![1, 2, 3];
while let Some(top) = stack.pop() { println!("{top}"); }   // 3, 2, 1
```

**Irrefutable** patterns match any value (`x`, `(a, b)`), and are required by `let`, `for` and parameters. **Refutable** patterns can fail (`Some(x)`), and belong in `match`, `if let`, `while let` and `let ... else`. [18] `let Some(x) = opt;` is an error; write `let Some(x) = opt else { return };`. [18]

## Pattern syntax

```rust
match n {
    1 | 2 => "one or two",            // alternatives
    3..=9 => "single digit",          // inclusive range (numbers and chars only)
    _ => "other",                     // anything, without binding
}

struct Point { x: i32, y: i32 }
match p {
    Point { x, y: 0 } => println!("on the x axis at {x}"),   // destructure + literal
    Point { x: 0, y } => println!("on the y axis at {y}"),
    Point { x, y } => println!("at ({x}, {y})"),
}

let (first, .., last) = (1, 2, 3, 4, 5);   // .. skips the middle
```

[18] Arms are tried top to bottom and the first match wins. [5] [18] Nested enums and structs destructure the same way, as in `Message::ChangeColor(Color::Hsv(h, s, v))`. [18]

Two subtle points: [18]

- `_` never binds, but `_name` does. `let _s = s;` *moves* `s`; `let _ = s;` does not.
- `..` must be unambiguous: `(.., second, ..)` is an error, because Rust cannot tell which element you mean.

## Guards and @ bindings

```rust
let num = Some(4);
match num {
    Some(x) if x % 2 == 0 => println!("{x} is even"),
    Some(x) => println!("{x} is odd"),
    None => (),
}

match msg_id {
    id @ 3..=7 => println!("id in range: {id}"),   // test and bind at once
    10..=12 => println!("another range"),
    id => println!("other id: {id}"),
}
```

A **match guard** is an extra `if` after the pattern; the compiler does not consider guards when checking exhaustiveness. [18] With alternatives, the guard applies to all of them: `4 | 5 | 6 if y` means `(4 | 5 | 6) if y`. [18] `@` binds the matched value while also testing it against a pattern. [18]

## New since the Book chapter: let chains and if-let guards

The Book's patterns chapter says you cannot combine `if let Ok(age) = age && age > 30`. [18] That is no longer true: **let chains** were stabilized for the 2024 edition in Rust 1.88. [21] [22]

```rust
fn sum_first_two(nums: &[u8]) -> Option<u8> {
    let mut iter = nums.iter();
    if let Some(first) = iter.next()
        && let Some(second) = iter.next()
    {
        first.checked_add(*second)
    } else {
        None
    }
}
```

`if` and `while` conditions may chain any number of `let` patterns and boolean expressions with `&&`, but not `||`. [22] Rust 1.95 then stabilized **if-let guards** in `match` arms: [21]

```rust
match input {
    Some(s) if let Ok(n) = s.parse::<i32>() => println!("number {n}"),
    Some(s) => println!("text {s}"),
    None => println!("none"),
}
```

Both examples, and `if let Ok(age) = age && age > 30`, compiled on rustc 1.99.1 with edition 2024. [74] On older editions let chains are not available. [22]

:::key-takeaways
- Refutable patterns go in `match`, `if let`, `while let`, `let ... else`; irrefutable ones in `let`, `for`, parameters.
- Use `|`, `..=`, destructuring, `_`, `..`, guards and `@` to express the shape you expect.
- Edition 2024 adds let chains (`if let A = a && let B = b`) and Rust 1.95 adds `if let` guards.
:::

:::glossary
- **Pattern**: a description of a value's shape that may bind parts to names.
- **Destructuring**: breaking a struct, tuple or enum into its parts with a pattern.
- **Refutable pattern**: a pattern that might not match.
- **Irrefutable pattern**: a pattern that always matches.
- **Match guard**: an extra `if` condition on a match arm.
- **@ binding**: naming a value while also testing it against a pattern.
- **Let chain**: several `let` patterns and conditions joined with `&&` in one `if` or `while`.
- **if-let guard**: a match-arm guard of the form `if let PATTERN = expr`.
:::
