---
id: l31
title: "Tokio: tasks, Send, channels, select! and blocking work"
quiz: quiz-31.yaml
sources: [16, 47, 48, 49, 50, 51, 52, 74]
---
After this lesson you can spawn Tokio tasks, satisfy the `'static` and `Send` bounds they need, share state without holding locks across `.await`, coordinate tasks with channels and `select!`, and keep blocking work off the async threads.

## Setup

```toml
[dependencies]
tokio = { version = "1.54.1", features = ["full"] }
```

`full` turns on everything; real applications often enable only the features they use to cut compile time. [47]

## Tasks

```rust
#[tokio::main]
async fn main() {
    let handle = tokio::spawn(async {
        // runs concurrently with main
        "return value"
    });
    let out = handle.await.unwrap();
    println!("GOT {out}");
}
```

A Tokio **task** is an asynchronous green thread: `tokio::spawn` hands an async block to the scheduler and returns a `JoinHandle`; awaiting it gives a `Result`, which is `Err` if the task panicked or was cancelled at shutdown. [48] Tasks are cheap, about one allocation and 64 bytes, so spawning thousands or millions is normal. [48] The default runtime is multi-threaded and may move a task to another thread at any `.await`. [48] [49] In the Book's words, the runtime manages tasks the way the OS manages threads, and many runtimes use **work stealing** to balance tasks across threads. [16]

### The 'static bound

A spawned task may outlive the function that spawned it, so it cannot borrow that function's locals; the compiler error (E0373) suggests `async move`. [48] As in Chapter 7, `T: 'static` does not mean "lives forever", only "owns its data". [48] Data needed by several tasks is shared with `Arc`. [48]

### The Send bound

Because the scheduler may move tasks between threads, everything a task holds **across an `.await`** must be `Send`. [48]

```rust
tokio::spawn(async {
    let rc = std::rc::Rc::new("hello");
    tokio::task::yield_now().await;   // rc is still alive here...
    println!("{rc}");                 // ...so the future is not Send: compile error
});
```

Scoping `rc` so it is dropped before the `.await` fixes it. [48]

## Shared state: which Mutex?

The Tokio tutorial uses `Arc<std::sync::Mutex<HashMap<..>>>` and explains: a synchronous mutex is fine in async code as long as contention is low and the lock is **not held across an `.await`**. [49] `std::sync::MutexGuard` is not `Send`, so holding one across an `.await` inside a spawned task is a compile error, and the fix is to end the guard's scope with a block before the `.await`. [49] The tutorial notes that calling `drop(guard)` instead is not enough, because the compiler decides `Send`-ness from scopes; that was still true when this course tested it on rustc 1.99.1. [49] [74] The cleanest pattern is to lock only inside small non-async methods. [49] `tokio::sync::Mutex` can be held across `.await` but is more expensive; for heavy contention, prefer a task that owns the state and receives messages, or shard the lock. [49] Lab 5 follows this advice with a `std::sync::RwLock`.

## Channels

| Channel | Producers / consumers | Values |
|---|---|---|
| `mpsc` | many / one | many, bounded capacity |
| `oneshot` | one / one | exactly one |
| `broadcast` | many / many | every receiver sees every value |
| `watch` | many / many | only the latest value |

[50] The **manager task** pattern: one task owns a resource (say, a connection) and receives commands over `mpsc`; each command carries a `oneshot::Sender` for the reply. [50] `mpsc::channel(32)` is bounded: once 32 messages are queued, `send(...).await` waits, which gives **backpressure**, so unbounded queues cannot eat all your memory. [50] `recv()` returns `None` when every sender is dropped. [50]

## select! and cancellation

```rust
tokio::select! {
    val = rx1 => println!("rx1 completed first with {val:?}"),
    val = rx2 => println!("rx2 completed first with {val:?}"),
}
```

`select!` waits on several async expressions and runs the branch of the first to complete; the others are **dropped**. [51] In async Rust, dropping a future *is* cancellation: it will never be polled again. [51] It supports up to 64 branches and picks the first branch to poll at random. [51]

## Blocking and CPU-heavy work

A future yields only at `.await`, so a long computation or a blocking call stalls every task on that worker thread. [16] Tokio's `spawn_blocking` runs a closure on a separate pool of threads where blocking is acceptable; such tasks cannot be aborted, and for CPU-bound workloads a dedicated executor like `rayon` may be a better fit. [52] The Book's rule of thumb: threads for work that is very parallelizable (CPU-bound), async for work that is very concurrent (I/O-bound), and the two combine well. [16]

:::key-takeaways
- `tokio::spawn` needs `'static` (use `async move`) and `Send` across every `.await`.
- A std `Mutex` is fine if never held across `.await`; otherwise restructure, use a manager task, or `tokio::sync::Mutex`.
- Bounded `mpsc` gives backpressure; `select!` cancels the losers by dropping them; blocking work goes to `spawn_blocking`.
:::

:::glossary
- **Task**: a unit of async work scheduled by the runtime, like a lightweight thread.
- **Green thread**: a thread managed by a library instead of the operating system.
- **Work stealing**: idle worker threads taking queued tasks from busy ones.
- **Contention**: many tasks or threads competing for the same lock.
- **Backpressure**: slowing producers down when consumers cannot keep up.
- **oneshot channel**: a channel for exactly one value, often used for replies.
- **Cancellation**: stopping an async operation, done in Rust by dropping its future.
- **spawn_blocking**: Tokio's way to run blocking code on a separate thread pool.
- **Shard**: split one shared structure into several, each with its own lock.
:::
