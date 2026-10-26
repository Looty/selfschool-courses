---
id: l26
title: Rc, Weak, RefCell and interior mutability
quiz: quiz-26.yaml
sources: [14, 24, 29, 30]
---
After this lesson you can share ownership with `Rc`, mutate through a shared reference with `Cell` and `RefCell`, combine them as `Rc<RefCell<T>>`, and avoid reference-cycle leaks with `Weak`.

## Rc<T>: shared ownership, one thread

Sometimes a value has several owners, such as a graph node pointed to by many edges, and you cannot tell at compile time which one finishes last. `Rc<T>` ("reference counted") keeps a count of owners and frees the value when the count reaches zero. [14] It is the analogue of a non-thread-safe `shared_ptr`.

```rust
use std::rc::Rc;

let a = Rc::new(vec![5, 10]);
let b = Rc::clone(&a);                 // count: 2, no deep copy
{
    let c = Rc::clone(&a);             // count: 3
    println!("{}", Rc::strong_count(&a));
}                                      // c dropped: count back to 2
```

`Rc::clone(&a)` is the idiomatic spelling: it makes clear this only bumps a counter, unlike a deep `clone`. [14] [29] `Rc` uses non-atomic counting, which is cheap but not thread-safe, so `Rc` does not implement `Send` and the compiler stops you from sending one to another thread; the thread-safe version is `Arc` (Chapter 11). [29] An `Rc` gives only shared access to its contents. [29]

## Interior mutability: Cell and RefCell

Rust's base rule is *aliasing XOR mutability*: many `&T` or one `&mut T`. [30] Some designs need mutation through a shared reference; the `cell` types allow it in a controlled way. [30]

- `Cell<T>` moves values in and out: `get` (for `Copy` types), `set`, `replace`, `take`. You can never get a reference to the inside, so no borrow can be invalidated. Prefer it for small `Copy` values. [30]
- `RefCell<T>` hands out borrows checked **at run time**: `borrow()` returns a `Ref<T>`, `borrow_mut()` a `RefMut<T>`, and breaking the one-writer-or-many-readers rule panics instead of failing to compile. [14] [30]

```rust
use std::cell::RefCell;

let log = RefCell::new(Vec::new());
log.borrow_mut().push("start");          // mutable borrow, ends at the semicolon
let first = log.borrow()[0];             // shared borrow
// let a = log.borrow_mut(); let b = log.borrow_mut();  // would panic: already borrowed
```

The Book's example is a mock object in a test: a `send(&self, msg)` method that must record messages even though the trait gives it only `&self`. Storing the messages in a `RefCell<Vec<String>>` solves it. [14] The cost is a small runtime check and bugs found later, at run time; the standard library calls interior mutability "something of a last resort". [14] [30] None of the cell types are `Sync`; across threads use `Mutex`, `RwLock` or atomics. [30]

## Rc<RefCell<T>>: shared and mutable

```rust
use std::cell::RefCell;
use std::rc::Rc;

let value = Rc::new(RefCell::new(5));
let a = Rc::clone(&value);
let b = Rc::clone(&value);
*value.borrow_mut() += 10;
println!("{} {}", a.borrow(), b.borrow());    // 15 15
```

Several owners, each able to mutate, with the borrow rules checked at run time. [14]

## Cycles leak, Weak breaks them

Rust's guarantees do not include freedom from memory leaks; a leak is memory safe. [14] [24] Two `Rc`s pointing at each other (possible once `RefCell` allows mutation) keep each other's counts above zero forever. [14]

`Weak<T>`, made with `Rc::downgrade(&rc)`, points to the value without owning it; it increments the *weak* count, which does not keep the value alive. [14] To use it, call `upgrade()`, which returns `Option<Rc<T>>`: `None` if the value is already gone. [14] The standard pattern for trees is strong `Rc` pointers from parents to children and `Weak` pointers from children back to parents. [29]

```rust
use std::cell::RefCell;
use std::rc::{Rc, Weak};

struct Node {
    value: i32,
    parent: RefCell<Weak<Node>>,
    children: RefCell<Vec<Rc<Node>>>,
}
```

:::key-takeaways
- `Rc<T>` = several owners on one thread; `Rc::clone` only increments a count.
- `Cell` and `RefCell` allow mutation through `&T`; `RefCell` checks borrows at run time and panics on violations.
- Cycles of `Rc` leak; use `Weak` for back-pointers and `upgrade()` to use them.
:::

:::glossary
- **Rc**: a reference-counted pointer that lets several owners share one value on one thread.
- **Reference count**: the number of owners currently pointing at a value.
- **Interior mutability**: changing data through a shared reference, with checks moved to run time or made impossible to misuse.
- **Cell**: a container you mutate by moving values in and out, never by reference.
- **RefCell**: a container that tracks borrows at run time.
- **Weak**: a non-owning pointer to an `Rc` value that may already be gone.
- **upgrade**: turning a Weak into an Rc if the value still exists.
- **Memory leak**: memory that is never freed although nothing will use it again.
- **Mock object**: a fake used in tests that records how it was called.
:::
