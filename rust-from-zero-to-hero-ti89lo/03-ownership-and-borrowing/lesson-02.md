---
id: l08
title: References and borrowing
quiz: quiz-08.yaml
sources: [3, 7, 28, 30, 60]
---
After this lesson you can pass values by shared and mutable reference, state the borrowing rule precisely, and explain why the compiler accepts or rejects a given borrow.

## Borrowing instead of moving

```rust
fn calculate_length(s: &String) -> usize {
    s.len()
}   // s goes out of scope, but it owns nothing, so nothing is dropped

let s1 = String::from("hello");
let len = calculate_length(&s1);   // s1 is still ours
```

`&s1` creates a **reference**: like a pointer it holds an address, but unlike a raw pointer it is guaranteed to point to a valid value of its type for as long as it is used. [3] Creating a reference is called **borrowing**. [3] References are immutable by default; to modify through one you need a mutable reference, `&mut`, and the variable itself must be `mut`: [3]

```rust
fn change(s: &mut String) { s.push_str(", world"); }

let mut s = String::from("hello");
change(&mut s);
```

## The rule

At any given time you can have **either** one mutable reference **or** any number of immutable references to a value, and references must always be valid. [3] The standard library states the same rule as aliasing XOR mutability: many `&T`, or one `&mut T`, never both. [30]

```rust
let mut s = String::from("x");
let r1 = &mut s;
let r2 = &mut s;          // error[E0499]: cannot borrow `s` as mutable more than once
println!("{r1} {r2}");
```

The payoff is that data races are impossible. A data race happens when two pointers access the same data at the same time, at least one of them writes, and nothing synchronizes them; the result is undefined behavior, and Rust refuses to compile code that could cause one. [3]

There is a performance payoff too. The Rustonomicon shows a function taking `input: &u32` and `output: &mut u32`: because a `&mut` can never alias another reference, the compiler may keep `*input` in a register across writes to `*output`, an optimization most languages cannot make without whole-program analysis. [28]

## How long does a borrow last?

A reference's scope starts where it is created and ends at its **last use**, not at the closing brace. [3] So this compiles:

```rust
let mut s = String::from("hello");
let r1 = &s;
let r2 = &s;
println!("{r1} and {r2}");   // last use of r1 and r2
let r3 = &mut s;             // fine: no shared borrow is still alive
r3.push('!');
```

This behavior comes from **non-lexical lifetimes** (NLL), designed in RFC 2094: the borrow checker computes how long a reference is live from the program's control flow, instead of from its enclosing block. [60] The RFC distinguishes a value's *scope* (until it is freed) from a reference's *lifetime* (the code where the reference may still be used); a reference's lifetime may never outlast its referent's scope. [60]

## No dangling references

```rust
fn dangle() -> &String {
    let s = String::from("hello");
    &s                       // s is dropped here, so this would dangle
}
```

This is rejected; the message says the return type contains a borrowed value "but there is no value for it to be borrowed from". The fix is to return the `String` itself and move ownership out. [3]

## A classic case: holding a reference while growing a Vec

```rust
let mut v = vec![1, 2, 3];
let first = &v[0];
v.push(4);                   // error[E0502]
println!("{first}");
```

Adding an element may reallocate the vector's buffer, which would leave `first` pointing into freed memory, so the shared borrow blocks the mutable one. [7] Copy the value out (`let first = v[0];`) or finish using the reference first.

:::key-takeaways
- `&T` borrows to read; `&mut T` borrows to write; neither takes ownership.
- One `&mut` or many `&`, never both at once: this rules out data races at compile time.
- A borrow lasts until its last use (non-lexical lifetimes), and can never outlive the value.
:::

:::glossary
- **Reference**: a pointer that the compiler guarantees is valid while it is used.
- **Borrowing**: creating a reference to a value you do not own.
- **Mutable reference**: `&mut T`, an exclusive reference that allows changes.
- **Aliasing**: two or more references pointing at the same memory.
- **Data race**: unsynchronized access to the same memory from two threads, at least one writing.
- **NLL (non-lexical lifetimes)**: the rule that a borrow ends at its last use, computed from control flow.
- **Dangling reference**: a reference to memory that has already been freed.
- **Register**: a tiny, very fast storage slot inside the CPU.
:::
