---
id: l30
title: Futures, async/await and Pin
quiz: quiz-30.yaml
sources: [16, 37, 47, 51, 62]
---
After this lesson you can explain what a Rust future is, why futures do nothing until awaited, why you need a runtime, how an `async fn` becomes a state machine, and why `Pin` exists.

## Concurrency vs parallelism

Concurrency is making progress on several tasks by switching between them; parallelism is running them at literally the same time on several cores. [16] Threads give you both but cost an OS thread each. Async gives concurrency for **I/O-bound** work, such as waiting on the network, without a thread per task. [16]

## Futures and async

A **future** is a value that may become ready later; in Rust it is any type implementing the `Future` trait. [16] `async fn` and `async { }` blocks produce futures, and `.await` waits for one, written after the expression so chains read left to right. [16]

```rust
async fn say_world() { println!("world"); }

#[tokio::main]
async fn main() {
    let op = say_world();   // nothing printed yet
    println!("hello");
    op.await;               // now "world" is printed
}
```

This prints `hello` then `world`. [47] Rust futures are **lazy**: calling an async function only creates the future, and the compiler warns if you never use it. [16] [47] That differs from languages where calling an async function starts the work immediately; in Rust the future *is* the computation, and whoever owns it drives it by polling. [51]

An `async fn` is roughly a normal function returning `impl Future<Output = T>` whose body is an `async move` block. [16]

## You need a runtime

`main` cannot itself be `async`: error E0752. Something must drive the top-level future, and that something is a **runtime**, which Rust deliberately does not bundle. [16] Different runtimes fit different targets, from servers with many cores to single-core microcontrollers with no heap. [16] Tokio is the most widely used, especially for web applications. [16] Its `#[tokio::main]` attribute rewrites `async fn main` into a normal `main` that builds a runtime and calls `block_on` on your code. [47]

## State machines and polling

```rust
pub trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
pub enum Poll<T> { Ready(T), Pending }
```

The compiler turns each async block into an anonymous type, essentially an enum with one state per `.await` point, holding the variables that live across that point. [16] [51] The runtime's **executor** calls `poll`. `Pending` means "not yet"; before returning it, the future arranges for the `Waker` from `cx` to be called when it can make progress, and the executor polls it again then. [51] `Ready(v)` delivers the result, and a finished future should not be polled again. [16]

Two consequences:

- A future only yields at `.await`. Long CPU work between awaits blocks every other future on that thread ("starving" them); insert yield points or move the work off the async thread. [16]
- Inside one async block, awaits run in order. Concurrency comes from combining futures, for example with `join!` (wait for all) or `select!` (first to finish), or from spawning tasks. [16]

## Why Pin

A state machine can hold a reference to one of its own fields, for example a borrow taken before an `.await` and used after it. Moving such a value would leave that internal pointer aimed at the old location. [16] [37] Rust values can normally be moved freely at any time, so something has to promise that this one will not move. [37]

`Pin<P>` wraps a pointer and guarantees the **pointee** stays at the same address until it is dropped; `Pin<Box<T>>` pins the `T`, while the `Box` itself can still move. [37] [16] Most types do not care about moving, so they implement the auto trait `Unpin`, and pinning them changes nothing; compiler-generated futures may be `!Unpin`. [16] Pinning is a library contract, not compiler magic, and safe code cannot misuse it unsoundly. [37]

In practice you meet `Pin` in error messages, for example when storing different futures in a `Vec<Pin<Box<dyn Future<Output = ()>>>>` (fix with `Box::pin(fut)` or `pin!`); `.await` pins for you. [16]

Pin's own designers acknowledge the difficulty. Saoirse Shepherd (without.boats) calls it a "complexity cliff", attributes much of it to `Pin` being a library type without language support for reborrowing or field projection, and has proposed "pinned places" as an improvement. [62]

:::key-takeaways
- A future does nothing until polled; `.await` polls it; a runtime such as Tokio drives the top level.
- `async fn` compiles to a state machine; it yields only at `.await` points.
- `Pin` keeps self-referential futures in place; you mostly see it in errors and fix it with `Box::pin`.
:::

:::glossary
- **Future**: a value representing a result that may be ready later.
- **async / await**: syntax to write futures like normal code; `.await` waits for a future.
- **Runtime**: a library that runs futures, schedules tasks and provides async I/O.
- **Executor**: the part of a runtime that polls futures.
- **Poll**: asking a future to make progress; it answers Ready or Pending.
- **Waker**: a handle a future uses to tell the executor it can make progress again.
- **I/O-bound**: limited by waiting for input/output, such as network or disk.
- **Starvation**: one task hogging the thread so others cannot progress.
- **Pin**: a wrapper guaranteeing the pointed-to value will not be moved.
- **Unpin**: the auto trait for types that are fine to move even when pinned.
- **Self-referential**: holding a pointer to part of itself.
:::
