---
id: l28
title: Shared state with Mutex, Arc, atomics, Send and Sync
quiz: quiz-28.yaml
sources: [15, 22, 27, 35, 36, 41, 65]
---
After this lesson you can share mutable state between threads with `Arc<Mutex<T>>`, use atomics for simple counters, handle lock poisoning, and explain how `Send` and `Sync` make data races a compile-time error.

## Mutex<T>: the lock owns the data

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..10 {
    let counter = Arc::clone(&counter);
    handles.push(thread::spawn(move || {
        let mut num = counter.lock().unwrap();   // MutexGuard<i32>
        *num += 1;
    }));                                          // guard dropped: unlocked
}
for h in handles { h.join().unwrap(); }
println!("Result: {}", *counter.lock().unwrap());   // Result: 10
```

In Rust the mutex *contains* the data: a `Mutex<i32>` is not an `i32`, so the only way to the value is `lock()`, and you cannot forget to lock. [15] `lock()` returns a `MutexGuard` that dereferences to the data and unlocks when dropped, so you cannot forget to unlock either. [15] [35]

Why `Arc` and not `Rc`? With `Rc` the compiler stops you: "`Rc<Mutex<i32>>` cannot be sent between threads safely", because its reference count is not updated atomically. [15] `Arc` ("atomically reference counted") has the same API with thread-safe counting, at some extra cost. [15] [41] `Arc` makes *ownership* shareable but does not make the contents thread-safe; that is why it is paired with `Mutex`. [41] `Mutex` gives interior mutability across threads, the way `RefCell` does on one thread. [15]

## Poisoning and guard scope

If a thread panics while holding the lock, the mutex is **poisoned**, and later `lock()` calls return an `Err`; `unwrap()` there spreads the panic so no thread sees possibly broken data. [35] Poisoning is advisory: `PoisonError::into_inner` still gives you the guard if you decide the data is fine. [35]

Hold locks briefly. Release a guard early with an inner block or `drop(guard)`; a guard created as a temporary, such as `*m.lock().unwrap() += 1;`, is dropped at the end of the statement. [35] Mara Bos warns about one trap: in `if let` and `match`, a guard in the condition lives until the end of the whole statement, not just the condition. [65] Rust cannot prevent **deadlocks**, two threads each waiting for a lock the other holds; they are not undefined behavior, just bugs. [15] [27]

## Atomics

For a counter or a flag, a mutex is more than you need. `std::sync::atomic` offers `AtomicUsize`, `AtomicBool` and friends, which are safe to share and can live in a plain `static`: [36] [22]

```rust
use std::sync::atomic::{AtomicU64, Ordering};

static REQUESTS: AtomicU64 = AtomicU64::new(0);

fn handle() {
    REQUESTS.fetch_add(1, Ordering::Relaxed);
}
```

Rust's atomics follow the C++20 memory model, and each operation takes an `Ordering` (`Relaxed`, `Acquire`, `Release`, `AcqRel`, `SeqCst`) with the same meaning as in C++. [36] They are lock-free where available but not guaranteed wait-free. [36] The 2024 edition guide recommends exactly this, or a `Mutex` or `LazyLock` in a `static`, instead of `static mut`. [22]

## Send and Sync

Two marker traits, built into the language, carry the thread-safety rules: [15]

- **`Send`**: ownership of a value can be transferred to another thread. Almost everything is `Send`; `Rc` and raw pointers are not.
- **`Sync`**: a value can be referenced from several threads at once; formally `T: Sync` if `&T: Send`. `Rc`, `RefCell` and `Cell` are not `Sync`; `Mutex` is.

A type made only of `Send` (or `Sync`) parts is automatically `Send` (or `Sync`). [15] `thread::spawn` requires its closure to be `Send`, which is how `Rc` across threads becomes a compile error. [15] Implementing either trait by hand requires `unsafe`, because the compiler cannot check the promise. [15] [27] The standard library's definition of a data race (conflicting, unsynchronized accesses with at least one non-atomic write) is undefined behavior, and these traits are what keeps safe code from producing one. [36]

:::key-takeaways
- `Arc<Mutex<T>>` is the standard way to share mutable state; the guard unlocks on drop.
- Keep guards short-lived; watch `if let`/`match` conditions; deadlocks are still possible.
- `Send` and `Sync` are auto traits the compiler checks, so sharing non-thread-safe types does not compile.
:::

:::glossary
- **Mutex**: a lock that lets one thread at a time access the data it guards.
- **MutexGuard**: the value `lock()` returns; it gives access and unlocks when dropped.
- **Arc**: a reference-counted pointer whose count is updated atomically, safe across threads.
- **Poisoning**: a mutex marking itself suspect after a thread panicked while holding it.
- **Deadlock**: threads waiting on each other forever.
- **Atomic**: an operation or type that other threads see as happening all at once.
- **Memory ordering**: the rule for how atomic operations are seen relative to other memory operations.
- **Send**: the trait for types that may move to another thread.
- **Sync**: the trait for types that may be shared by reference between threads.
- **Marker trait**: a trait with no methods that only states a property.
:::
