---
id: l07
title: Ownership, moves and drop
quiz: quiz-07.yaml
sources: [3, 4, 14, 20, 25]
---
After this lesson you can apply the three ownership rules, predict when a value is moved, copied or dropped, and choose between moving, cloning and `Copy` types.

## The three rules

1. Each value in Rust has an owner.
2. There can only be one owner at a time.
3. When the owner goes out of scope, the value is dropped. [3]

Dropping means calling the type's cleanup code, its `drop` function, at the closing brace. The Book points out that this is the pattern C++ calls RAII (Resource Acquisition Is Initialization). [3] What Rust adds is that the compiler tracks who the owner is.

## What a String looks like

A `String` is three words on the stack (a pointer to a heap buffer, a length and a capacity), plus the bytes on the heap. [3] That shape explains moves.

```rust
let s1 = String::from("hello");
let s2 = s1;              // copy the 3 stack words, not the heap bytes
// println!("{s1}");      // error[E0382]: borrow of moved value: `s1`
```

If both `s1` and `s2` stayed valid, both would free the same buffer at the end of the scope: a double free. Rust instead considers `s1` moved and no longer usable, so only `s2` frees the memory. [3] A move is a shallow copy plus invalidation of the source, checked at compile time. [3]

Rust never makes deep copies automatically, so any implicit copy is cheap. [3] When you want a deep copy, ask for it:

```rust
let s3 = s2.clone();      // new heap buffer; s2 and s3 both valid
```

A visible `.clone()` is a signal that something potentially expensive happens. [3]

## Copy types

```rust
let x = 5;
let y = x;     // x is still valid
```

Integers, `bool`, floats, `char`, and tuples or arrays made only of such types implement the `Copy` trait: assignment duplicates the bits and the original stays valid. [3] A type cannot be `Copy` if it, or any part of it, implements `Drop`, because a value that needs cleanup must have one owner. [3] You can derive `Copy` (together with `Clone`) for your own types when all their fields are `Copy`. [20]

## Functions move too

Passing a value to a function moves or copies it, exactly like assignment; returning a value moves ownership to the caller. [3]

```rust
fn takes(s: String) { /* s dropped at the end */ }
fn gives() -> String { String::from("yours") }

let a = String::from("hi");
takes(a);            // a is moved; using it now is an error
let b = gives();     // b owns the returned String
```

Passing ownership in and out of every function would be tedious; the next lesson's references solve that. [3] Struct update syntax moves too: `let u2 = User { email: e, ..u1 };` moves any non-`Copy` fields out of `u1`. [4]

## When exactly drop runs

- Locals are dropped in reverse order of declaration when their scope ends. [25] [14]
- Assigning a new value to a variable drops the old value first. [3] [25]
- A struct's fields are dropped in declaration order after its own `drop`. [25]
- To drop something early, call `std::mem::drop(value)`; calling the `Drop::drop` method yourself is not allowed (error E0040), because Rust would then drop the value a second time. [14]

```rust
struct Noisy(&'static str);
impl Drop for Noisy {
    fn drop(&mut self) { println!("drop {}", self.0); }
}
let _a = Noisy("a");
let _b = Noisy("b");
// end of scope prints: drop b, then drop a
```

:::key-takeaways
- One owner; the owner going out of scope drops the value (RAII, enforced by the compiler).
- Assignment and argument passing move non-`Copy` values; the source becomes unusable.
- `clone()` is the explicit deep copy; `Copy` types are duplicated implicitly because they are cheap and need no cleanup.
:::

:::glossary
- **Owner**: the variable responsible for freeing a value.
- **Drop**: running a value's cleanup code when its owner goes away.
- **RAII**: tying a resource's lifetime to an object so cleanup happens automatically at scope end.
- **Move**: handing ownership to another variable; the old one can no longer be used.
- **Shallow copy**: copying only a pointer and metadata, not the data it points to.
- **Deep copy**: copying the pointed-to data as well.
- **Double free**: freeing the same memory twice, which corrupts the heap.
- **Copy trait**: marks types that are duplicated by copying bits, leaving the original usable.
- **Capacity**: how much heap space a String or Vec has reserved, which may exceed its length.
:::
