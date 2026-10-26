---
id: l20
title: Closures and the Fn traits
quiz: quiz-20.yaml
sources: [12, 19, 21]
---
After this lesson you can write closures, predict how they capture their environment, use `move`, and choose between `Fn`, `FnMut` and `FnOnce` in your own signatures.

## Closures capture their environment

A closure is an anonymous function you can store in a variable or pass as an argument; unlike a function, it can use variables from the scope where it is defined. [12]

```rust
let threshold = 10;
let over = |x: i32| x > threshold;     // captures `threshold`
assert!(over(11));

let add_one = |x| x + 1;               // types inferred from the first use...
let two = add_one(1);                  // ...here: x is an i32
```

Parameter and return types are usually inferred. Once inferred from the first call they are fixed: calling the same closure later with a different type is an error. [12] Annotations are allowed, as in `|x: u32| -> u32 { x + 1 }`. [12]

## Three ways to capture

A closure captures each variable in the least demanding way its body needs: by shared reference, by mutable reference, or by value. [12]

```rust
let mut list = vec![1, 2, 3];

let print = || println!("{list:?}");    // borrows list immutably
print();

let mut push = || list.push(4);         // borrows list mutably
push();                                 // no other use of list allowed until push is done

let consume = move || list;             // `move` forces capture by value
let owned = consume();                  // list now lives in `owned`
```

`move` makes the closure take ownership of everything it uses even if the body only reads; this is how you hand data to another thread, which may outlive the current function (Chapter 11). [12]

## Fn, FnMut, FnOnce

What a closure's body does with captured values decides which of three traits it implements; they are additive: [12]

| Trait | The closure... | Can be called |
|---|---|---|
| `FnOnce` | may move a captured value out | once (every closure implements this) |
| `FnMut` | may mutate captured values but not move them out | many times |
| `Fn` | neither mutates nor moves out (or captures nothing) | many times, even concurrently |

Pick the most permissive bound your function can work with: [12]

```rust
// Option::unwrap_or_else calls f at most once, so it accepts any closure:
//     pub fn unwrap_or_else<F: FnOnce() -> T>(self, f: F) -> T
// slice::sort_by_key calls its closure once per element, so it needs FnMut.

let mut calls = 0;
let mut rects = vec![(10, 1), (3, 5), (7, 12)];
rects.sort_by_key(|r| { calls += 1; r.0 });   // FnMut: mutates `calls`
```

A closure that moves a captured `String` into a vector on each call only implements `FnOnce`, so `sort_by_key` rejects it. [12]

## Functions as values

Named functions work where a closure is expected: `opt.unwrap_or_else(Vec::new)`. [12] Plain function pointers have the type `fn(i32) -> i32` (lowercase) and implement all three closure traits; prefer generic `F: Fn(...)` parameters so callers can pass either, and use `fn` types mainly for interop with C, which has no closures. [19] Enum variant constructors are functions too: `(0..3).map(Status::Value)`. [19]

## Returning closures

Every closure has its own unnameable type, so return one with `impl Fn`: [19]

```rust
fn make_adder(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n
}
```

Two closures with the same signature still have different types; to return either of them, or to store several in one `Vec`, box them as trait objects: `Box<dyn Fn(i32) -> i32>`. [19]

Async closures, `async |x| ...`, were stabilized in Rust 1.85. [21]

:::key-takeaways
- Closures capture by `&`, `&mut` or value as needed; `move` forces by-value capture.
- `FnOnce` ⊇ `FnMut` ⊇ `Fn`: accept the loosest bound your code can use.
- Return closures as `impl Fn`; use `Box<dyn Fn>` for mixed closures.
:::

:::glossary
- **Closure**: an anonymous function that can capture variables from its surroundings.
- **Capture**: how a closure gets access to an outside variable: borrow or ownership.
- **move closure**: a closure that takes ownership of everything it captures.
- **Fn / FnMut / FnOnce**: the traits that say whether a closure may be called repeatedly and whether it mutates or consumes captures.
- **Function pointer**: a value of type `fn(...) -> ...` pointing to a named function.
- **Opaque type**: a type the compiler knows but you cannot name, as with `impl Trait`.
:::
