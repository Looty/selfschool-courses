---
id: l29
title: "Lab 3: parallel file checksums"
quiz: quiz-29.yaml
resources: [../resources/lab3-checksums/Cargo.toml, ../resources/lab3-checksums/src/lib.rs, ../resources/lab3-checksums/src/main.rs, ../resources/lab3-checksums/src/bin/gen.rs]
sources: [1, 2, 15, 32, 45]
---
After this lab you will have generated 256 MiB of test data, hashed it on one thread and on all your CPU cores with scoped threads and a channel, checked that both give the same answer, and compared their speed in debug and release builds.

This is a hands-on lab using only the standard library. It was built and run with rustc 1.99.1 on a 20-thread Windows machine while writing this course.

## Shortcut: the ready-made files

Download the four files into `checksums/`, keeping `src/` and `src/bin/`. Then:

```bash
cargo test                          # 2 tests
cargo run --release --bin gen       # writes data/file00.bin .. file63.bin (64 x 4 MiB)
cargo run --release                 # sequential vs parallel, release build
cargo run                           # the same, debug build
```

What we saw (your times will differ):

```text
64 files in data
combined checksum: 7ae813a0ca3662a4
1 thread:  313.1503ms
20 threads: 47.0266ms
```

The **combined checksum must be exactly `7ae813a0ca3662a4`** on every machine: the generator uses a fixed seed. The very first release run took 767 ms on one thread because the files were not yet in the operating system's cache; the second run gave the numbers above. The debug build took 942 ms on one thread and 110 ms on 20, showing why benchmarks use `--release`. [1] [45]

## Step 1: a hash that is quick to write

`fnv1a` loops over the bytes with `wrapping_mul`. The wrapping is intentional: the algorithm relies on modular arithmetic, and plain `*` would panic on overflow in debug builds. [2] The unit test checks two published FNV-1a values.

## Step 2: the sequential version

```rust
files.iter().map(|p| Ok((p.clone(), checksum_file(p)?))).collect()
```

`collect` can build a `Result<Vec<_>, _>` from an iterator of `Result`s: it stops at the first error, so `?` inside the closure propagates I/O failures.

## Step 3: the parallel version

```rust
let chunk_size = files.len().div_ceil(threads).max(1);
let (tx, rx) = mpsc::channel();

thread::scope(|s| {
    for chunk in files.chunks(chunk_size) {
        let tx = tx.clone();
        s.spawn(move || {
            for path in chunk {
                let result = checksum_file(path).map(|sum| (path.clone(), sum));
                tx.send(result).expect("receiver alive");
            }
        });
    }
});
drop(tx);
```

- `thread::scope` lets every worker **borrow** its `chunk` of the caller's slice: no copying of the file list, and the scope joins all workers before returning. [32]
- `move` moves only the cloned sender `tx` and the `chunk` slice reference into each thread. [15]
- Results travel back over an `mpsc` channel. The original `tx` is dropped after the scope, so the receiver's iterator ends once the last worker's clone is gone. [15]
- Results arrive in whatever order threads finish, so they are sorted before comparing.

## Step 4: why the speedup is less than 20x

Each file is read from disk before it is hashed, the work is split into only 20 chunks, and threads finish at different times. Measure before you parallelize, and measure in release mode. [1]

## Check yourself

- Change `threads` to 1, 2, 4 and 8 in `main.rs`. How does the time scale?
- Replace `wrapping_mul` with `*` and run `cargo run` (debug). What happens, and why does `cargo run --release` behave differently? [2] [45]
- Remove `drop(tx);`. What happens, and why?

:::key-takeaways
- `thread::scope` + `chunks` splits borrowed data across threads without cloning it.
- Clone the channel sender per worker and drop the original so the receiver can finish.
- Check that parallel and sequential results agree; benchmark only release builds.
:::

:::glossary
- **Checksum / hash**: a short number computed from data, used to detect changes.
- **FNV-1a**: a simple, fast, non-cryptographic hash function.
- **Seed**: the starting value of a pseudo-random generator; the same seed gives the same data.
- **File cache**: memory where the operating system keeps recently read files.
- **Speedup**: how many times faster the parallel version is than the sequential one.
- **Chunk**: one of the pieces a slice is split into by `chunks(n)`.
:::
