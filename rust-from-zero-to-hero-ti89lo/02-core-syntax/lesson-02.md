---
id: l05
title: Expressions, functions and control flow
quiz: quiz-05.yaml
sources: [2, 19]
---
After this lesson you can write functions that return values without `return`, use `if` and the three loops (with labels and `break` values), and predict when a stray semicolon breaks your code.

## Almost everything is an expression

Rust separates **statements**, which perform an action and produce no value, from **expressions**, which evaluate to a value. [2] `let y = 6;` is a statement, so you cannot write `let x = (let y = 6);` and, unlike C, there is no `x = y = 6` chaining. [2] Blocks, `if`, function calls and macro calls are all expressions. [2]

```rust
let y = {
    let x = 3;
    x + 1      // no semicolon: this is the block's value, 4
};
```

Adding a semicolon to the last line turns it into a statement, and the block then evaluates to `()`. [2]

## Functions

```rust
fn add_one(x: i32) -> i32 {
    x + 1          // the final expression is the return value
}
```

Parameter types are always written; that is a deliberate design choice so that types elsewhere can be inferred. [2] The return type follows `->`, and the value of the last expression is returned; `return` is only needed to leave early. [2] Function names use `snake_case`, and a function may be defined before or after the code that calls it. [2]

The classic beginner error is a semicolon after the last expression:

```rust
fn plus_one(x: i32) -> i32 {
    x + 1;   // error[E0308]: mismatched types, expected i32, found ()
}
```

The body now ends in a statement, so it evaluates to `()`, and the compiler suggests removing the semicolon. [2]

## if is an expression

```rust
let n = 7;
let kind = if n % 2 == 0 { "even" } else { "odd" };
```

The condition must be a `bool`, and when `if` produces a value, every arm must have the same type. [2] There is no ternary operator because `if` already does the job.

## Loops

Rust has three loops. [2]

```rust
// loop: forever, until break; break can carry a value out
let mut counter = 0;
let result = loop {
    counter += 1;
    if counter == 10 { break counter * 2; }   // result = 20
};

// while: loop while a condition holds
let mut n = 3;
while n != 0 { n -= 1; }

// for: iterate over anything iterable
for i in (1..4).rev() { println!("{i}"); }    // 3, 2, 1
```

`for` over a collection is the idiomatic default: it cannot run past the end and avoids a bounds check per step that a manual index loop would need. [2] Nested loops can be labelled, and `break 'outer;` or `continue 'outer;` then applies to the labelled loop instead of the innermost one. [2]

A `loop` with no `break` never finishes, so its type is `!`, the **never type**; so are `continue` and `panic!`. [19] Because `!` can stand in for any type, a `match` arm that does `continue` can sit next to an arm that produces a number. [19]

:::key-takeaways
- Statements end in `;` and produce nothing; expressions produce values; the last expression of a block is its value.
- A function returns its final expression; an extra `;` there gives a "found ()" error.
- `if` and `loop` produce values; `for` over an iterator is the default loop.
:::

:::glossary
- **Expression**: code that evaluates to a value.
- **Statement**: code that performs an action and has no value, usually ending in a semicolon.
- **Block**: code inside `{ }`, which evaluates to its last expression.
- **Range**: a sequence of numbers such as `1..4` (excludes 4) or `1..=4` (includes 4).
- **Loop label**: a name like `'outer` that `break` and `continue` can target.
- **Never type / `!`**: the type of expressions that never finish, such as an endless loop.
- **snake_case**: the naming style with lowercase words joined by underscores.
:::
