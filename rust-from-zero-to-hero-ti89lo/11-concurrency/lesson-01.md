---
id: l27
title: Threads, move closures, scoped threads and channels
quiz: quiz-27.yaml
sources: [15, 32, 65]
---
After this lesson you can start and join threads, move data into them, borrow local data safely with scoped threads, and pass messages between threads with channels.

## Spawning threads

```rust
use std::thread;
use std::time::Duration;

let handle = thread::spawn(|| {
    for i in 1..5 {
        println!("hi {i} from the spawned thread");
        thread::sleep(Duration::from_millis(1));
    }
});

for i in 1..3 {
    println!("hi {i} from main");
    thread::sleep(Duration::from_millis(1));
}
handle.join().unwrap();   // wait for the spawned thread
```

The standard library uses one operating-system thread per Rust thread (a 1:1 model). [15] When `main` returns, all spawned threads are shut down, finished or not, so you keep the `JoinHandle` and call `join` to wait. [15] The interleaving of the output is up to the OS scheduler and changes between runs. [15]

## move closures

```rust
let v = vec![1, 2, 3];
let handle = thread::spawn(move || {
    println!("vector: {v:?}");    // v now belongs to the thread
});
handle.join().unwrap();
```

Without `move`, the closure would only borrow `v`, and the compiler rejects that: it cannot know whether the thread will outlive `v`, and the help text suggests `move`. [15] With `move`, ownership goes to the thread, so the main thread can no longer use or drop `v`; the borrow checker still enforces the ownership rules. [15]

## Scoped threads: borrowing without moving

Since Rust 1.63, `thread::scope` lets threads borrow local data, because every thread spawned in the scope is joined before `scope` returns. [32]

```rust
let mut a = vec![1, 2, 3];
let mut x = 0;

thread::scope(|s| {
    s.spawn(|| println!("first thread sees {a:?}"));   // shared borrow of a
    s.spawn(|| x += a[0] + a[2]);                      // mutable borrow of x
});

a.push(4);                       // borrows ended with the scope
assert_eq!(x, a.len());          // 4
```

The usual borrowing rules still apply across the threads: several may read `a`, and only one may mutate `x`. [32] If an automatically joined thread panicked, `scope` itself panics. [32] Mara Bos's *Rust Atomics and Locks* sums it up: this pattern guarantees no thread spawned in the scope can outlive it. [65] Lab 3 uses scoped threads so each worker can borrow a slice of the file list instead of copying it.

## Channels

"Do not communicate by sharing memory; instead, share memory by communicating", a slogan the Book quotes from Go's documentation. [15] `std::sync::mpsc` provides **multiple-producer, single-consumer** channels: [15]

```rust
use std::sync::mpsc;

let (tx, rx) = mpsc::channel();
let tx2 = tx.clone();                       // a second producer

thread::spawn(move || {
    for word in ["hi", "from", "one"] { tx.send(word.to_string()).unwrap(); }
});
thread::spawn(move || {
    tx2.send("hello from two".to_string()).unwrap();
});

for msg in rx {                             // ends when every sender is dropped
    println!("got: {msg}");
}
```

`send` takes ownership of the value, so the sending thread cannot touch it afterwards; that is exactly what prevents it from changing data another thread is reading. [15] `send` returns an error if the receiver is gone. [15] `recv` blocks until a message arrives and returns an error once all senders are dropped; `try_recv` returns immediately; and iterating over the receiver stops when the channel closes. [15]

:::key-takeaways
- `thread::spawn` + `join`; spawned threads die when `main` ends.
- `move` transfers ownership into a thread; `thread::scope` lets threads borrow locals safely.
- `mpsc` channels move values between threads; iteration over the receiver ends when all senders drop.
:::

:::glossary
- **Thread**: an independent path of execution inside a program, scheduled by the OS.
- **JoinHandle**: the value `spawn` returns; `join` waits for the thread to finish.
- **Scoped thread**: a thread guaranteed to finish before a given scope ends, so it may borrow local data.
- **Channel**: a queue for sending values from one thread to another.
- **mpsc**: multiple producer, single consumer: many senders, one receiver.
- **Producer / consumer**: the side that sends messages / the side that receives them.
- **Block**: to wait, doing nothing, until something happens.
:::
