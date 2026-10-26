---
id: l34
title: Unsafe Rust, undefined behavior, Miri and FFI
quiz: quiz-34.yaml
sources: [19, 22, 23, 27, 31, 58]
---
After this lesson you can say exactly what `unsafe` allows, list the main kinds of undefined behavior, wrap unsafe code in a sound safe API, check it with Miri, and call C from Rust and Rust from C.

## What unsafe allows, and what it does not

Inside an `unsafe` block you gain five abilities, the "unsafe superpowers": [19] [27]

1. Dereference a raw pointer (`*const T`, `*mut T`).
2. Call an `unsafe` function or method (including C functions).
3. Access or modify a mutable `static`.
4. Implement an `unsafe` trait (such as `Send` or `Sync`).
5. Access fields of a `union`.

That is all. `unsafe` does **not** turn off the borrow checker or other checks; references inside it are still checked. [19] Google reports the same from Android: `unsafe{}` "doesn't actually disable all or even most of Rust's safety checks". [58]

The keyword has two meanings: on a function or trait it *declares* a contract the compiler cannot check; on a block or impl it *asserts* that you checked it. [27] The Reference is clear that avoiding undefined behavior becomes your job, and that Rust programs must still never cause it. [23]

## Undefined behavior

Among the behaviors the Reference lists as undefined: [23]

- data races;
- accessing memory through a dangling or misaligned pointer;
- breaking the aliasing rules (memory behind a live `&T` must not change unless inside `UnsafeCell`; a live `&mut T` must be the only way to reach its memory);
- producing an invalid value, such as a `bool` that is not 0 or 1, a `char` in the surrogate range, a null reference or `Box`, or an enum with an invalid discriminant;
- calling a function with the wrong ABI.

The list "is not exhaustive", since Rust has no complete formal model yet. [23] Undefined behavior affects the whole program, including code reached through FFI. [23]

## Sound abstractions

Code is **sound** if no safe caller can use it to cause UB, and **unsound** otherwise. [23] The standard pattern is a small `unsafe` block inside a safe function. The Book's example re-implements `split_at_mut`, which the borrow checker rejects in safe code because it cannot see that the two halves do not overlap: [19]

```rust
use std::slice;

fn split_at_mut(values: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = values.len();
    let ptr = values.as_mut_ptr();
    assert!(mid <= len);
    // SAFETY: mid <= len, so both halves are in bounds and do not overlap.
    unsafe {
        (
            slice::from_raw_parts_mut(ptr, mid),
            slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}
```

The `assert!` is what makes it sound. The Rustonomicon shows why safety is **non-local**: changing `<` to `<=` in a bounds check, an edit to purely safe code, can make neighboring unsafe code unsound. [27] Unsafe code that depends on a struct's invariants effectively makes the whole module responsible, which is why privacy at the module boundary is the main tool for containing it. [27] Writing a `// SAFETY:` comment explaining why each unsafe operation is fine is the idiomatic habit. [19]

## Raw pointers and static mut

```rust
let mut num = 5;
let r1 = &raw const num;   // *const i32: creating raw pointers is safe
let r2 = &raw mut num;     // *mut i32
unsafe {
    *r2 += 1;
    println!("{}", *r1);   // 6: dereferencing needs unsafe
}
```

Raw pointers may be null, may dangle, ignore borrowing rules, and are never freed automatically. [19] In the 2024 edition, taking a reference to a `static mut` is denied by default, because merely creating such a reference in violation of the aliasing rules is immediate UB; prefer atomics, a `Mutex`, or `LazyLock`/`OnceLock` in a normal `static`. [22]

## Miri

Miri is the Rust project's tool for detecting undefined behavior by running your program or tests in an interpreter. [19] It needs nightly: [19]

```bash
rustup +nightly component add miri
cargo +nightly miri test
```

Miri only checks code paths that actually run, so a clean run is evidence, not proof. [19]

## FFI

```rust
unsafe extern "C" {
    safe fn abs(input: i32) -> i32;            // promised safe: no unsafe block needed
    unsafe fn strlen(p: *const std::ffi::c_char) -> usize;
}

#[unsafe(no_mangle)]
pub extern "C" fn call_from_c() {
    println!("Just called a Rust function from C!");
}
```

In the 2024 edition `extern` blocks must be written `unsafe extern`; individual items can be marked `safe` or `unsafe`, and unmarked items are unsafe to call. [22] Marking an item `safe` is a promise you must keep. [19] `#[unsafe(no_mangle)]` keeps the symbol name, so C can find it; the attribute is unsafe because unmangled names can collide. [19] A `Box<T>` has the same representation as a C `T*`, so `extern "C"` Rust functions may take or return `Box<T>`, and `Option<Box<T>>` for a nullable pointer; but do not use `Box` for pointers that C allocated. [31]

:::key-takeaways
- `unsafe` unlocks five operations; every other rule, including borrow checking, still applies.
- Wrap unsafe code in small, documented (`// SAFETY:`) blocks inside safe, sound APIs; privacy contains the risk.
- Use Miri on tests that exercise unsafe code; in 2024 write `unsafe extern` and `#[unsafe(no_mangle)]`.
:::

:::glossary
- **unsafe block**: code where the five extra operations are allowed and the programmer vouches for safety.
- **Raw pointer**: `*const T` or `*mut T`, a pointer with no validity or borrowing guarantees.
- **Undefined behavior (UB)**: an operation with no defined meaning, after which anything may happen.
- **Sound**: unsafe code that no safe caller can misuse to cause UB.
- **Invariant**: a condition that must always hold, such as "len is not more than capacity".
- **Miri**: a Rust interpreter that detects undefined behavior while running code.
- **FFI (foreign function interface)**: calling code written in another language, usually C.
- **Name mangling**: the compiler encoding extra information into symbol names.
- **union**: a type whose fields share the same memory; reading a field is unsafe.
:::
