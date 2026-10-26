---
id: l25
title: Box, Deref and Drop
quiz: quiz-25.yaml
sources: [14, 31, 66]
---
After this lesson you can put values on the heap with `Box`, build recursive types, write a type that behaves like a reference through `Deref`, and explain deref coercion.

## Smart pointers

A reference just borrows. A **smart pointer** is a struct that acts like a pointer but has extra capabilities and usually *owns* what it points to; `String` and `Vec` are smart pointers too. [14] What makes them pointer-like are two traits: `Deref` (use it like a reference) and `Drop` (custom cleanup). [14]

## Box<T>: single ownership on the heap

`Box<T>` stores a `T` on the heap and keeps only a pointer on the stack; when the box goes out of scope, both are freed. [14] For a C++ programmer it plays the role of `unique_ptr`: one owner, freed automatically, moved rather than copied. It has no overhead beyond the heap allocation. [14] Use it when: [14]

- a type's size cannot be known at compile time but you need a fixed-size value (recursive types);
- you want to move a large value without copying its bytes;
- you want a value of "some type implementing a trait" (`Box<dyn Trait>`, Chapter 6).

```rust
#[derive(Debug)]
enum List {
    Cons(i32, Box<List>),
    Nil,
}
use List::{Cons, Nil};

let list = Cons(1, Box::new(Cons(2, Box::new(Nil))));
println!("{list:?}");   // Cons(1, Cons(2, Nil))
```

Without the `Box`, `List` would contain itself directly and have infinite size; the compiler says so and suggests adding "indirection (e.g., a `Box`, `Rc`, or `&`)". [14] A `Box<T>` for a sized `T` is exactly one pointer and has the same representation and C ABI as a `T*`. [31] It never allocates more than `isize::MAX` bytes. [31]

## Deref: treat it like a reference

```rust
use std::ops::Deref;

struct MyBox<T>(T);

impl<T> Deref for MyBox<T> {
    type Target = T;
    fn deref(&self) -> &T { &self.0 }
}

let x = 5;
let y = MyBox(x);
assert_eq!(5, *y);   // *y is really *(y.deref())
```

Implementing `Deref` lets `*` work on your type: Rust replaces `*y` with `*(y.deref())`, once per `*` in your code. [14] `deref` returns a reference rather than the value so that dereferencing does not move the value out of the smart pointer. [14]

## Deref coercion

When you pass a reference to a function expecting a different reference type, Rust applies `deref` as many times as needed to make the types match, at compile time and with no runtime cost. [14]

```rust
fn hello(name: &str) { println!("Hello, {name}!"); }

let m = MyBox(String::from("Rust"));
hello(&m);     // &MyBox<String> -> &String -> &str
```

Without it you would write `hello(&(*m)[..])`. [14] Coercion happens from `&T` to `&U` when `T: Deref<Target = U>`, from `&mut T` to `&mut U` with `DerefMut`, and from `&mut T` to `&U`; never from `&T` to `&mut U`, because a shared reference cannot be proven unique. [14] The API Guidelines reserve `Deref` for smart pointers; using it to fake inheritance is discouraged. [66]

## Drop: custom cleanup

```rust
struct Connection { name: String }

impl Drop for Connection {
    fn drop(&mut self) { println!("closing {}", self.name); }
}

let c = Connection { name: "db".into() };
drop(c);                         // std::mem::drop: close it now
println!("after close");
```

`Drop` is in the prelude; its `drop(&mut self)` runs automatically when the value goes out of scope. [14] You may not call `c.drop()` yourself (error E0040), since Rust would then drop it a second time; `std::mem::drop(c)` moves the value in and drops it early. [14] Releasing a lock early is the classic use. [14]

:::key-takeaways
- `Box<T>` is single ownership on the heap, one pointer wide; use it for recursion, big moves and trait objects.
- `Deref` makes `*` and method calls work; deref coercion turns `&MyBox<String>` into `&str` for free.
- `Drop` runs cleanup automatically; use `std::mem::drop` to run it early.
:::

:::glossary
- **Smart pointer**: a struct that acts like a pointer and adds behavior such as ownership or counting.
- **Box**: a smart pointer that owns one heap-allocated value.
- **Recursive type**: a type that contains a value of its own type, such as a list node.
- **Indirection**: reaching a value through a pointer instead of storing it inline.
- **Deref trait**: lets a type be dereferenced with `*` like a reference.
- **Deref coercion**: automatic conversion between reference types using `Deref`.
- **Drop trait**: lets a type run code when it is destroyed.
- **ABI**: the low-level calling convention that decides how values are passed between compiled code.
:::
