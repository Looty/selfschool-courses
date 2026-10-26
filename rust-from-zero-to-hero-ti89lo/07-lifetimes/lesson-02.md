---
id: l18
title: "Lifetimes in structs, 'static, and the borrow checker's limits"
quiz: quiz-18.yaml
sources: [7, 9, 14, 48, 60, 61, 70, 74]
---
After this lesson you can write structs that hold references, use `'static` correctly, avoid the most common lifetime misconceptions, and recognize code that is safe but still rejected by today's borrow checker.

## Structs that borrow

A struct that holds a reference needs a lifetime parameter, and the annotation means an instance can never outlive the data it refers to. [9]

```rust
struct Excerpt<'a> {
    part: &'a str,
}

impl<'a> Excerpt<'a> {
    fn level(&self) -> i32 { 3 }
    fn announce(&self, note: &str) -> &str {   // elision rule 3: output tied to self
        println!("note: {note}");
        self.part
    }
}

let novel = String::from("Call me Ishmael. Some years ago...");
let first = novel.split('.').next().unwrap();
let e = Excerpt { part: first };     // e cannot outlive `novel`
```

The lifetime must be declared after `impl` and used after the type name, because it is part of the type. [9] Owned fields (`String`, not `&str`) avoid lifetime parameters entirely, which is why the Book recommends them while you learn. [9]

## 'static

`'static` means a reference can live for the entire program; every string literal is a `&'static str` stored in the binary. [9] When an error message suggests adding `'static`, the real problem is usually a dangling reference or mismatched lifetimes; fix that instead. [9]

As a **bound**, `T: 'static` means something different: the type contains no non-static borrows, so the value *could* be kept around forever. An owned `String` or `Vec<u8>` satisfies `T: 'static` and can still be dropped at any time. [70] [48] You will meet this bound in Chapter 11 and 12: `thread::spawn` and `tokio::spawn` require it because the new thread or task might outlive the function that created it. [48]

## Common misconceptions

A widely read community post lists misconceptions such as: [70]

- "If `T: 'static`, `T` must live for the whole program." False: owned data meets the bound.
- "My code has no lifetimes because I wrote none." Elision means nearly every function with references is generic over lifetimes.
- "If it compiles, my annotations are right." The borrow checker guarantees memory safety, not that the annotation expresses what you meant; a too-strict signature may compile and still be painful to call.
- "Lifetimes grow and shrink at run time." They are fixed at compile time.

## Safe code the borrow checker still rejects

The borrow checker is conservative: it would rather reject a correct program than accept an incorrect one. [14] RFC 2094 (non-lexical lifetimes) fixed many false rejections, but its own "problem case #3" was left open: a borrow returned out of the function on one branch. [60]

```rust
use std::collections::HashMap;
use std::hash::Hash;

fn get_default<'r, K: Hash + Eq + Copy, V: Default>(map: &'r mut HashMap<K, V>, key: K) -> &'r mut V {
    match map.get_mut(&key) {
        Some(value) => value,
        None => {
            map.insert(key, V::default());     // error[E0499]
            map.get_mut(&key).unwrap()
        }
    }
}
```

On the `None` path nothing is borrowed any more, so the code is safe; but because the `Some` path returns the borrow to the caller, today's checker treats `map` as borrowed for `'r` on every path. This was checked on rustc 1.99.1, which still reports E0499. [74] The idiomatic fix is the entry API, which the RFC notes was partly motivated by this very limitation: [60] [7]

```rust
fn get_default<K: Hash + Eq, V: Default>(map: &mut HashMap<K, V>, key: K) -> &mut V {
    map.entry(key).or_default()
}
```

Other known limits: a method that borrows all of `self` blocks access to other fields even if it only uses one; the RFC suggests splitting such methods across the fields themselves or using free functions that take the fields separately. [60]

## Polonius: the next borrow checker

The Rust project's next-generation analysis, **Polonius Alpha**, is flow-sensitive and accepts this kind of code. In August 2026 it was enabled by default on nightly, with stabilization aimed "prior to the end of the year". [61] It does not include everything the older experimental Polonius accepted. [61]

:::low-confidence
Polonius Alpha was nightly-only when this course was written (October 2026). Check the Rust blog or release notes before assuming stable Rust accepts the first `get_default` above. [61]
:::

:::key-takeaways
- A struct holding `&'a T` cannot outlive the borrowed data; prefer owned fields while learning.
- `&'static` means "lives for the whole program"; `T: 'static` only means "contains no short borrows".
- Some safe code is still rejected (NLL problem case #3); reach for APIs like `entry`, and watch for Polonius on stable.
:::

:::glossary
- **'static**: the lifetime of the whole program run.
- **T: 'static bound**: a requirement that a type holds no borrowed data with a shorter lifetime.
- **Conservative analysis**: a checker that may reject valid code so that it never accepts invalid code.
- **Entry API**: HashMap methods that look up a key once and then insert or modify in place.
- **Flow-sensitive**: an analysis that considers which path through the code is taken.
- **Polonius**: the next-generation borrow checker being developed by the Rust project.
- **Free function**: a function that is not a method of any type.
:::
