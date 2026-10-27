# Sources

Numbers are stable: lessons and questions cite them as `[n]`. Never renumber; append new sources at the end.
Only sources actually read during research are listed. "The Book" is The Rust Programming Language, read from its source repository (rust-lang/book, main branch, October 2026), which matches the edition published at doc.rust-lang.org/book.

1. [The Rust Programming Language, ch. 1: Getting Started](https://doc.rust-lang.org/book/ch01-00-getting-started.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
   - Notes: rustup install, `rustc --version`, `cargo new` layout (edition = "2024"), `cargo build/run/check`, `--release`, Cargo.lock.
2. [The Rust Programming Language, ch. 3: Common Programming Concepts](https://doc.rust-lang.org/book/ch03-00-common-programming-concepts.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
   - Notes: immutability by default, const, shadowing, scalar types, integer overflow (debug panic, release wrap; checked/wrapping/overflowing/saturating), char is 4 bytes, arrays and out-of-bounds panic, statements vs expressions, if/loop/while/for, loop labels.
3. [The Rust Programming Language, ch. 4: Understanding Ownership](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
   - Notes: ownership rules, String layout (pointer, length, capacity), move vs clone vs Copy, drop and RAII, references, the one-mutable-or-many-shared rule, data race definition, dangling references, slices and `&str`.
4. [The Rust Programming Language, ch. 5: Using Structs](https://doc.rust-lang.org/book/ch05-00-structs.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
   - Notes: struct syntax, field init shorthand, struct update syntax moves, tuple and unit structs, derive(Debug), dbg!, methods and `self` forms, associated functions, automatic referencing (no `->`).
5. [The Rust Programming Language, ch. 6: Enums and Pattern Matching](https://doc.rust-lang.org/book/ch06-00-enums.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
   - Notes: enums with data, Option instead of null (Hoare quote), exhaustive match, `_`, if let, let...else.
6. [The Rust Programming Language, ch. 7: Packages, Crates, and Modules](https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
   - Notes: crate vs package, binary and library crates, module lookup rules, privacy defaults, pub on structs vs enums, paths, use idioms, pub use re-exports, `mod` is not an include.
7. [The Rust Programming Language, ch. 8: Common Collections](https://doc.rust-lang.org/book/ch08-00-common-collections.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
   - Notes: Vec indexing vs get, reallocation and borrowing, String as UTF-8 bytes, no string indexing, bytes/chars/graphemes, HashMap ownership, entry API, SipHash.
8. [The Rust Programming Language, ch. 9: Error Handling](https://doc.rust-lang.org/book/ch09-00-error-handling.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
   - Notes: no exceptions, panic unwinding vs abort, RUST_BACKTRACE, Result, unwrap vs expect, `?` with From conversion, `?` on Option, main returning Result, when to panic, validation types.
9. [The Rust Programming Language, ch. 10: Generic Types, Traits, and Lifetimes](https://doc.rust-lang.org/book/ch10-00-generics.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
   - Notes: generics, monomorphization, traits, default methods, orphan rule, impl Trait, trait bounds and where, blanket impls, lifetime annotations, the three elision rules, 'static.
10. [The Rust Programming Language, ch. 11: Writing Automated Tests](https://doc.rust-lang.org/book/ch11-00-testing.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: #[test], assert macros, should_panic, Result tests, parallel test threads, filtering, ignore, unit vs integration tests, tests/common/mod.rs, thin main.rs.
11. [The Rust Programming Language, ch. 12: An I/O Project](https://doc.rust-lang.org/book/ch12-00-an-io-project.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (searched for the args, error-handling, env var and stderr passages)
    - Notes: std::env::args panics on invalid Unicode (args_os), process::exit, Box<dyn Error> from run, IGNORE_CASE env var, eprintln! for errors.
12. [The Rust Programming Language, ch. 13: Iterators and Closures](https://doc.rust-lang.org/book/ch13-00-functional-features.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: closure capture modes, move, FnOnce/FnMut/Fn, Iterator trait, laziness, adapters vs consumers, benchmark loop vs iterator (19,620,300 vs 19,234,900 ns/iter), zero-cost abstractions.
13. [The Rust Programming Language, ch. 14: More about Cargo and Crates.io](https://doc.rust-lang.org/book/ch14-00-more-about-cargo.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: profiles and opt-level, doc comments and doc tests, pub use for public API, publishing is permanent, yank, workspaces with one Cargo.lock, cargo install, cargo-something subcommands.
14. [The Rust Programming Language, ch. 15: Smart Pointers](https://doc.rust-lang.org/book/ch15-00-smart-pointers.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: Box and recursive types, Deref and deref coercion rules, Drop and std::mem::drop, Rc, RefCell runtime borrow panics, Rc<RefCell<T>>, leaks via cycles are memory safe, Weak.
15. [The Rust Programming Language, ch. 16: Fearless Concurrency](https://doc.rust-lang.org/book/ch16-00-concurrency.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: 1:1 threads, JoinHandle, move closures, mpsc channels, Mutex and MutexGuard, Rc is not Send, Arc, Send and Sync.
16. [The Rust Programming Language, ch. 17: Async and Await](https://doc.rust-lang.org/book/ch17-00-async-await.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: concurrency vs parallelism, futures are lazy, async fn desugaring, runtimes not bundled, state machines, await points and starvation, Future::poll, Pin and Unpin, streams, threads vs tasks rules of thumb.
17. [The Rust Programming Language, ch. 18: Object-Oriented Programming Features](https://doc.rust-lang.org/book/ch18-00-oop.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: no inheritance, trait objects with dyn, static vs dynamic dispatch, state pattern, encoding states as types.
18. [The Rust Programming Language, ch. 19: Patterns and Matching](https://doc.rust-lang.org/book/ch19-00-patterns.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: where patterns appear, refutability, ranges, destructuring, `_` vs `_x`, `..`, match guards, `@` bindings. Its remark that `if let` conditions cannot be combined with `&&` predates let chains (see [21]).
19. [The Rust Programming Language, ch. 20: Advanced Features](https://doc.rust-lang.org/book/ch20-00-advanced-features.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: five unsafe superpowers, raw pointers and &raw, split_at_mut, unsafe extern and `safe` items, #[unsafe(no_mangle)], static mut, SAFETY comments, Miri, associated types, operator overloading, fully qualified syntax, supertraits, newtype, never type, DSTs, function pointers, macro_rules! and procedural macros.
20. [The Rust Programming Language, appendices C, D and E](https://doc.rust-lang.org/book/appendix-00.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full (C, D, E)
    - Notes: derivable traits (Debug, PartialEq/Eq, PartialOrd/Ord, Clone/Copy, Hash, Default), rustfmt, cargo fix, Clippy approx_constant example, rust-analyzer, four editions.
21. [Rust release notes (RELEASES.md)](https://github.com/rust-lang/rust/blob/master/RELEASES.md) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (Language and Cargo sections of 1.85.0 to 1.99.1)
    - Notes: 1.85.0 (2025-02-20) Rust 2024 stable and async closures; 1.86.0 trait upcasting; 1.88.0 let chains in the 2024 edition; 1.95.0 if-let guards on match arms; 1.97.0 build.warnings; 1.99.0 (2026-10-01) new `debug` profile; 1.99.1 released 2026-10-15.
22. [The Rust Edition Guide](https://doc.rust-lang.org/edition-guide/) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (What are editions, Creating a project, Transitioning, Rust 2024 index, let chains, unsafe extern, static mut references, unsafe_op_in_unsafe_fn, prelude, gen keyword)
    - Notes: opt-in per crate, crates of all editions interoperate, valid editions 2015/2018/2021/2024, migration steps with cargo fix --edition, Rust 2024 = 1.85.0 (RFC 3501), static_mut_refs deny and its alternatives.
23. [The Rust Reference: Behavior considered undefined](https://doc.rust-lang.org/reference/behavior-considered-undefined.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: list of UB (data races, dangling or misaligned access, aliasing rules, invalid values), sound vs unsound, list not exhaustive.
24. [The Rust Reference: Behavior not considered unsafe](https://doc.rust-lang.org/reference/behavior-not-considered-unsafe.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: deadlocks, leaks, integer overflow rules (panic with debug assertions, otherwise panic or two's complement wrap), logic errors are not UB.
25. [The Rust Reference: Destructors](https://doc.rust-lang.org/reference/destructors.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (intro, drop scopes, local variables, temporary scopes)
    - Notes: drop order (fields in declaration order, locals in reverse), assignment drops the old value, 2024 edition temporary scope changes.
26. [The Rust Reference: Trait objects and dyn compatibility](https://doc.rust-lang.org/reference/types/trait-object.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (trait object types; the dyn compatibility section of Traits)
    - Notes: pointer + vtable, dyn required since 2021, dyn compatibility rules (formerly object safety).
27. [The Rustonomicon: Meet Safe and Unsafe; How Safe and Unsafe Interact; What Unsafe Rust Can Do; Working with Unsafe](https://doc.rust-lang.org/nomicon/meet-safe-and-unsafe.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full (these four chapters)
    - Notes: two languages in one, the soundness property, unsafe as contract declaration vs assertion, asymmetric trust and unsafe traits, what Rust considers safe (deadlocks, leaks, overflow), safety is non-local and privacy contains it.
28. [The Rustonomicon: Ownership and Aliasing](https://doc.rust-lang.org/nomicon/aliasing.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full (Ownership and Lifetimes intro; Aliasing)
    - Notes: dangling-pointer examples Rust rejects; why non-aliased &mut enables optimizations.
29. [std::rc module](https://doc.rust-lang.org/std/rc/index.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full (module docs)
    - Notes: non-atomic counting, not Send, Rc::clone idiom, Weak and cycles.
30. [std::cell module](https://doc.rust-lang.org/std/cell/index.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full (module docs)
    - Notes: aliasing XOR mutability, Cell/RefCell/OnceCell/LazyCell, thread-safe counterparts, interior mutability as a last resort.
31. [std::boxed module](https://doc.rust-lang.org/std/boxed/index.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full (module docs)
    - Notes: Box<T> is one pointer and C-ABI compatible with T*, Option<Box<T>> for nullable pointers, Box aliasing like &mut.
32. [std::thread::scope](https://doc.rust-lang.org/std/thread/fn.scope.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: scoped threads borrow non-'static data, all joined at scope end, stable since 1.63.0.
33. [std::option module](https://doc.rust-lang.org/std/option/index.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (overview, ?, representation, method overview)
    - Notes: no null references, null pointer optimization guarantees, combinators.
34. [std::result module](https://doc.rust-lang.org/std/result/index.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (overview, must_use, ?, method overview)
    - Notes: Result is #[must_use], ? propagation.
35. [std::sync::Mutex](https://doc.rust-lang.org/std/sync/struct.Mutex.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (description, poisoning, examples)
    - Notes: RAII guards, poisoning and into_inner, dropping guards early.
36. [std::sync::atomic module](https://doc.rust-lang.org/std/sync/atomic/index.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (overview, memory model, portability)
    - Notes: C++20 memory model, data race definition, lock-free not wait-free.
37. [std::pin module](https://doc.rust-lang.org/std/pin/index.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (moving, pinning, address sensitivity, Pin<Ptr>, pinning as a library contract)
    - Notes: values are trivially movable, self-referential async state machines, Pin pins the pointee.
38. [std::collections module](https://doc.rust-lang.org/std/collections/index.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (when to use which, performance table, capacity)
    - Notes: "you should probably just use Vec or HashMap", cost table, collections never shrink automatically.
39. [std::error::Error trait](https://doc.rust-lang.org/std/error/trait.Error.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (description, source, example)
    - Notes: Error requires Debug + Display, message style, source() chains, description deprecated.
40. [std::vec::Vec (Guarantees section)](https://doc.rust-lang.org/std/vec/struct.Vec.html#guarantees) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (Guarantees)
    - Notes: (pointer, capacity, length), no small-vector optimization, never shrinks automatically, push reallocates only when len == capacity.
41. [std::sync::Arc](https://doc.rust-lang.org/std/sync/struct.Arc.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (description, thread safety)
    - Notes: atomic counting cost, Send/Sync only if T is, Arc does not make T thread-safe, make_mut.
42. [The Cargo Book: Cargo.toml vs Cargo.lock](https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: who writes each file, "When in doubt, check Cargo.lock into the version control system", cargo update.
43. [The Cargo Book: Specifying Dependencies](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (crates.io dependencies and version requirement syntax)
    - Notes: default = caret requirement, 0.x compatibility rule, tilde, wildcard, comparison, pre-releases.
44. [The Cargo Book: Features](https://doc.rust-lang.org/cargo/reference/features.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (features table, default, optional dependencies, dependency features)
    - Notes: features off unless enabled, default-features = false, dep: prefix, serde derive feature.
45. [The Cargo Book: Profiles](https://doc.rust-lang.org/cargo/reference/profiles.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (default profiles)
    - Notes: dev and release defaults incl. overflow-checks, debug profile, test and bench inheritance.
46. [The Cargo Book: Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: partly (overview, root package, virtual workspace, members)
    - Notes: shared Cargo.lock and target directory, virtual manifests need `resolver`.
47. [Tokio tutorial: Hello Tokio](https://tokio.rs/tokio/tutorial/hello-tokio) · Tokio project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: features = ["full"], lazy async fn, what #[tokio::main] expands to.
48. [Tokio tutorial: Spawning](https://tokio.rs/tokio/tutorial/spawning) · Tokio project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: tasks as green threads, JoinHandle, 64 bytes per task, 'static bound, Send bound across .await.
49. [Tokio tutorial: Shared state](https://tokio.rs/tokio/tutorial/shared-state) · Tokio project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: std Mutex vs tokio Mutex, MutexGuard not Send across .await, scoping guards, contention strategies.
50. [Tokio tutorial: Channels](https://tokio.rs/tokio/tutorial/channels) · Tokio project · accessed 2026-10-26 · reliability: high · read: partly (to the backpressure section)
    - Notes: manager task pattern, mpsc/oneshot/broadcast/watch, bounded capacity, recv returns None when senders drop.
51. [Tokio tutorial: Select and Async in depth](https://tokio.rs/tokio/tutorial/select) · Tokio project · accessed 2026-10-26 · reliability: high · read: partly (select!, cancellation, syntax; futures, wakers, summary)
    - Notes: cancellation by dropping a future, 64-branch limit, wakers and polling.
52. [tokio::task::spawn_blocking](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html) · Tokio project · accessed 2026-10-26 · reliability: high · read: partly (description and notes)
    - Notes: run blocking work on a dedicated pool, cannot be aborted, rayon for CPU-bound work.
53. [Serde overview and Using derive](https://serde.rs/derive.html) · Serde project · accessed 2026-10-26 · reliability: high · read: full (overview and derive pages)
    - Notes: trait-based, no runtime reflection, features = ["derive"], troubleshooting duplicate serde versions with cargo tree -d.
54. [clap derive tutorial](https://docs.rs/clap/latest/clap/_derive/_tutorial/index.html) · clap project · accessed 2026-10-26 · reliability: high · read: partly (quick start, configuring the parser, positionals)
    - Notes: cargo add clap --features derive, #[derive(Parser)], #[command(version, about)], #[arg(short, long)], subcommands.
55. [axum crate documentation](https://docs.rs/axum/latest/axum/) · tokio-rs/axum · accessed 2026-10-26 · reliability: high · read: partly (overview to sharing state)
    - Notes: Router, handlers, extractors (Path, Query, Json), IntoResponse, State with Arc, tower middleware, axum::serve.
56. [thiserror crate documentation](https://docs.rs/thiserror/latest/thiserror/) · dtolnay/thiserror · accessed 2026-10-26 · reliability: high · read: full
    - Notes: derive(Error), #[error("...")], #[from], #[source], transparent, not part of public API.
57. [anyhow crate documentation](https://docs.rs/anyhow/latest/anyhow/) · dtolnay/anyhow · accessed 2026-10-26 · reliability: high · read: full
    - Notes: anyhow::Result for applications, context/with_context, downcasting, anyhow!/bail!, backtraces via env vars.
58. [Rust in Android: move fast and fix things](https://blog.google/security/rust-in-android-move-fast-fix-things/) · Google (Jeff Vander Stoep), 2025-11-13 · accessed 2026-10-26 · reliability: medium · read: partly (quoted passages through a fetch tool)
    - Notes: memory safety below 20% of Android vulnerabilities; Rust ~0.2 vulnerabilities per MLOC vs ~1,000 for C/C++; ~4x lower rollback rate; ~25% less review time; CVE-2025-48530 near miss; ~4% of Rust code in unsafe blocks. Medium because it is a vendor report on its own code base.
59. [We need a safer systems programming language](https://www.microsoft.com/en-us/msrc/blog/2019/07/we-need-a-safer-systems-programming-language) · Microsoft Security Response Center (Ryan Levick, Sebastian Fernandez), 2019-07-18 · accessed 2026-10-26 · reliability: medium · read: partly (quoted passages through a fetch tool)
    - Notes: "~70% of the vulnerabilities Microsoft assigns a CVE each year continue to be memory safety issues"; about a decade of data; modern C++ not completely memory safe. Medium: 2019 data, Microsoft products only.
60. [RFC 2094: Non-lexical lifetimes](https://rust-lang.github.io/rfcs/2094-nll.html) · Rust Project (Niko Matsakis), 2017 · accessed 2026-10-26 · reliability: high · read: partly (summary, motivation, problem cases 1 to 4, appendix on what NLL does not fix)
    - Notes: lifetime vs scope, control-flow based lifetimes, problem case #3 (conditional return of a borrow) not fixed; verified on rustc 1.99.1 that case #3 still fails with E0499.
61. [Enabling the next iteration of the borrow checker on nightly](https://blog.rust-lang.org/2026/08/04/enabling-polonius-alpha-on-nightly) · Rust Blog (Jack Huey), 2026-08-04 · accessed 2026-10-26 · reliability: high · read: partly (quoted passages through a fetch tool)
    - Notes: Polonius Alpha is flow-sensitive, enabled on nightly, stabilization aimed for before end of 2026, -Zpolonius=off to opt out; full Polonius not planned.
62. [Pin](https://without.boats/blog/pin/) · without.boats (Saoirse Shepherd), 2024-07-19 · accessed 2026-10-26 · reliability: medium · read: partly (through a fetch tool)
    - Notes: why Pin exists (self-references in async state machines), rejected alternatives, "complexity cliff", missing reborrowing and projections, pinned places proposal. Medium: single-author blog, though the author designed much of async Rust.
63. [Learn Rust With Entirely Too Many Linked Lists](https://rust-unofficial.github.io/too-many-lists/) · rust-unofficial · accessed 2026-10-26 · reliability: medium · read: partly (introduction)
    - Notes: "99% of the time you should just use a Vec"; topics: Box, Rc, Arc, raw pointers, Miri, unsafe. Medium: community tutorial.
64. [Rustlings](https://rustlings.rust-lang.org/setup/) · Rust Project · accessed 2026-10-26 · reliability: high · read: full (setup page and README)
    - Notes: cargo install rustlings, rustlings init, rustlings; use alongside the Book.
65. [Rust Atomics and Locks, ch. 1: Basics of Rust Concurrency](https://mara.nl/atomics/basics.html) · Mara Bos (O'Reilly, 2023, free online) · accessed 2026-10-26 · reliability: high · read: partly (through a fetch tool)
    - Notes: scoped threads, Rc vs Arc, Cell/RefCell/Mutex/RwLock/atomics/UnsafeCell, Send and Sync definitions, poisoning, MutexGuard temporaries in if let. Written before the 2024 edition's if-let scope change.
66. [Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html) · Rust Library Team · accessed 2026-10-26 · reliability: high · read: full
    - Notes: naming (as_/to_/into_, iter/iter_mut/into_iter), common traits, C-GOOD-ERR, C-NEWTYPE, C-CUSTOM-TYPE, C-STRUCT-PRIVATE, C-SEALED.
67. [Clippy documentation](https://doc.rust-lang.org/clippy/) · Rust Project · accessed 2026-10-26 · reliability: high · read: full (introduction page)
    - Notes: over 800 lints, categories and default levels, do not enable restriction wholesale. Commands verified locally (cargo clippy, --fix).
68. [Adopting the FLS](https://blog.rust-lang.org/2025/03/26/adopting-the-fls/) · Rust Blog (TC, Spec Team), 2025-03-26 · accessed 2026-10-26 · reliability: high · read: partly (through a fetch tool)
    - Notes: FLS by Ferrous Systems and AdaCore, adopted by the Rust Project, Reference status unchanged, used to qualify toolchains for safety-critical industries.
69. [Announcing Rust 1.0](https://blog.rust-lang.org/2015/05/15/Rust-1.0/) · Rust Blog, 2015-05-15 · accessed 2026-10-26 · reliability: high · read: partly (through a fetch tool)
    - Notes: breaking changes largely out of scope from 1.0, six-week train releases, control plus safety without a garbage collector.
70. [Common Rust Lifetime Misconceptions](https://github.com/pretzelhammer/rust-blog/blob/master/posts/common-rust-lifetime-misconceptions.md) · pretzelhammer, 2020-05-19 · accessed 2026-10-26 · reliability: medium · read: partly (the ten misconceptions and takeaways)
    - Notes: T: 'static does not mean "lives forever", &'a T vs T: 'a, elision makes most code generic over lifetimes, lifetimes are static. Medium: community blog post.
71. [rustup: Channels](https://rust-lang.github.io/rustup/concepts/channels.html) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: stable every 6 weeks, beta, nightly; rustup toolchain install nightly; components may be missing from some nightlies.
72. [rust-lang.org home page](https://www.rust-lang.org/) · Rust Project · accessed 2026-10-26 · reliability: high · read: full
    - Notes: tagline, performance/reliability/productivity, use areas.
73. [Rust 2027 edition discussion and draft edition cadence update](https://internals.rust-lang.org/t/we-have-only-two-years-to-prepare-the-rust-2027-edition/22494) · Rust Internals forum and an Edition Team draft (hackmd, 2026-08-02) · accessed 2026-10-26 · reliability: low · read: abstract only (search result summaries)
    - Notes: no accepted RFC for a next edition was found; a draft proposes decoupling editions from a fixed three-year cadence. Low: forum posts and a draft, not decisions.
74. [Observations from this course's own test runs on Rust 1.99.1](https://blog.rust-lang.org/2026/10/15/Rust-1.99.1/) · this course, run on rustc 1.99.1 / cargo 1.99.1 (x86_64-pc-windows-msvc), 2026-10-26 · reliability: high · read: full
    - Notes: let chains, trait upcasting, if-let guards, async closure syntax and thread::scope compile; u8 overflow method results; size_of::<&str>() = 16, String = 24, Option<Box<i32>> = 8 on x86_64; NLL problem case #3 rejected with E0499; a std MutexGuard released with drop() (not a block) before .await still makes a spawned Tokio future non-Send; an Rc held across .await in tokio::spawn fails with "future cannot be sent between threads safely"; every lab in resources/ built and tested; crate versions from cargo search: tokio 1.54.1, axum 0.8.9, clap 4.6.7, serde 1.0.229, serde_json 1.0.154, anyhow 1.0.104, thiserror 2.0.21; cargo fix removed a needless `mut` and renamed an unused variable to `_y`. These are this course's own measurements; the link is the announcement of the compiler version they were made with.
75. [RustAssistant: Using LLMs to Fix Compilation Errors in Rust Code](https://www.microsoft.com/en-us/research/publication/rustassistant-using-llms-to-fix-compilation-errors-in-rust-code/) · Microsoft Research (Deligiannis, Lal, Mehrotra, Poddar, Rastogi), ICSE 2025 · accessed 2026-10-27 · reliability: high · read: abstract only
    - Notes: prompting plus iteration between an LLM and the Rust compiler; peak accuracy of roughly 74% on real-world compilation errors in popular open-source Rust repositories; Rust's features "pose a steep learning curve for programmers". The per-dataset numbers in the earlier arXiv preprint (2308.05177) were not read and are not used.
76. [Type-Constrained Code Generation with Language Models](https://arxiv.org/abs/2504.09246) · Mündler, He, Wang, Sen, Song, Vechev, PLDI 2025 · accessed 2026-10-27 · reliability: high · read: abstract only
    - Notes: LLMs "frequently generate code with typing errors"; type-constrained decoding for TypeScript reduces compilation errors by more than half on HumanEval and MBPP.
77. [rustc dev guide: Errors and lints](https://rustc-dev-guide.rust-lang.org/diagnostics.html) · Rust Project · accessed 2026-10-27 · reliability: high · read: partly (suggestions, Applicability, JSON output)
    - Notes: Applicability levels MachineApplicable ("can be applied mechanically"), HasPlaceholders, MaybeIncorrect, Unspecified; --error-format json prints one JSON object per line for tools such as rustfix; a `rendered` field holds the human text.
78. [The Cargo Book: External tools](https://doc.rust-lang.org/cargo/reference/external-tools.html) · Rust Project · accessed 2026-10-27 · reliability: high · read: partly (JSON messages)
    - Notes: --message-format=json prints one JSON object per line; reasons compiler-message, compiler-artifact, build-script-executed, build-finished; rustc's own JSON is embedded in the message field.
79. [Go: Data Race Detector](https://go.dev/doc/articles/race_detector) · The Go Authors · accessed 2026-10-27 · reliability: high · read: full
    - Notes: enabled with -race; "only finds races that happen at runtime"; typical cost 5-10x memory and 2-20x execution time.
80. [cppreference: Undefined behavior](https://en.cppreference.com/w/cpp/language/ub) · cppreference.com · accessed 2026-10-27 · reliability: high · read: partly (definitions)
    - Notes: implementations "are not required to diagnose undefined behavior"; the program "is not required to do anything meaningful"; ill-formed, no diagnostic required.
81. [PEP 484: Type Hints](https://peps.python.org/pep-0484/) · van Rossum, Lehtosalo, Langa, 2014 · accessed 2026-10-27 · reliability: high · read: partly (rationale and goals)
    - Notes: no type checking happens at run time; checking is done by a separate offline checker; "Python will remain a dynamically typed language".
82. [TypeScript Handbook: The Basics](https://www.typescriptlang.org/docs/handbook/2/basic-types.html) · Microsoft · accessed 2026-10-27 · reliability: high · read: full
    - Notes: type annotations are erased and "never change the runtime behavior"; tsc emits JavaScript despite type errors unless noEmitOnError; the lenient default does not check null/undefined; strict turns the checks on.
83. [MultiPL-E: A Scalable and Extensible Approach to Benchmarking Neural Code Generation](https://arxiv.org/abs/2208.08227) · Cassano et al., 2022 · accessed 2026-10-27 · reliability: medium · read: partly (abstract and first part of the HTML version)
    - Notes: performance "is correlated with language popularity"; "static type-checking neither helps nor hinders"; Codex pass@1 45.9% on Python, Rust above 40% but reliably below Python. Medium: preprint, 2022, models of that time.
84. [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) · Anthropic (Erik Schluntz, Barry Zhang), 2024-12-19 · accessed 2026-10-27 · reliability: medium · read: partly (agents section and coding appendix)
    - Notes: agents need "ground truth" from the environment at each step, such as tool results or code execution; code solutions are verifiable through automated tests and agents iterate using test results. Medium: a vendor's engineering guide, not a study.
85. [Rust compiler performance survey 2025 results](https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results) · Rust Blog (Jakub Beránek, compiler performance working group), 2025-09-10 · accessed 2026-10-27 · reliability: high · read: full (through a fetch tool)
    - Notes: over 3,700 responses; average satisfaction 6 of 10; 55% wait more than ten seconds for a rebuild; about 45% of former users cited compile times as a reason they stopped; cargo check is the most common command after each change; incremental rebuilds are the main pain point.
86. [Observations from this course's own test runs on Rust 1.99.1, part 2](https://blog.rust-lang.org/2026/10/15/Rust-1.99.1/) · this course, run on rustc 1.99.1 (x86_64-pc-windows-msvc), 2026-10-27 · reliability: high · read: full
    - Notes: `rustc --edition 2024 --error-format=json --emit=metadata broken/move_error.rs` (Lab 1) printed error E0382 with a help child suggesting `.clone()` at line 4, suggestion_applicability MachineApplicable. The link is the announcement of the compiler version used.
