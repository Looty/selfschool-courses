---
id: l01
title: Why Rust
quiz: quiz-01.yaml
sources: [1, 3, 21, 22, 27, 58, 59, 68, 69, 72, 73]
---
After this lesson you can explain what problem Rust was built to solve, what "safe" and "unsafe" Rust mean, and how Rust changes without breaking your code.

## New to Rust? The 60-second version

Rust is a compiled systems language with no garbage collector and no runtime you have to ship. [72] Memory is managed by **ownership**: every value has exactly one owner, and the value is freed when its owner goes out of scope, much like RAII in C++. [3] Code can **borrow** a value through a reference instead of taking it; the compiler checks that borrows never outlive the value and never let two parts of the program write the same data at once. That checker is called the **borrow checker**. [3] Most of the rules you will meet in this course exist to make those checks possible at compile time, so they cost nothing at run time. [3] **Cargo** is the build tool and package manager, and a **crate** is one compiled library or program. [1]

## The problem: memory bugs in systems code

In 2019 Microsoft's security team reported that about 70% of the vulnerabilities Microsoft assigns a CVE each year are memory safety issues, a share that had stayed roughly the same for over a decade. [59] The same post argued that modern C++ is still not completely memory safe and data-race free. [59]

Google has published numbers from Android, which has been adding Rust next to its C and C++ code. In November 2025 it reported that memory safety bugs had fallen below 20% of Android's vulnerabilities for the first time. [58] It estimated about 0.2 memory safety vulnerabilities per million lines of Rust, against roughly 1,000 per million lines in its historical C and C++ data, and it reported a rollback rate for Rust changes about 4 times lower than for C++. [58]

:::low-confidence
Both figures come from companies measuring their own code bases, read here through quoted passages rather than the full raw data. Treat them as strong evidence for those code bases, not as universal constants. [58] [59]
:::

## Two languages in one: safe and unsafe Rust

The Rustonomicon, the official guide to unsafe code, describes Rust as two languages: **Safe Rust** and **Unsafe Rust**. [27] If you only write Safe Rust you never get a dangling pointer, a use-after-free or any other undefined behavior. [27] Its central promise, the *soundness property*, is: "No matter what, Safe Rust clients can't cause Undefined Behavior." [27]

Unsafe Rust is the same language with five extra abilities, such as dereferencing raw pointers and calling C functions, that the compiler cannot check. [27] You opt in with the `unsafe` keyword, so the places that need careful review are marked in the source. Google reported that about 4% of Android's Rust code sits inside unsafe blocks. [58] Chapter 13 covers unsafe Rust; until then, everything is safe code.

Rust also deliberately leaves some things to you: deadlocks, memory leaks and integer overflow are not "unsafe" in Rust's sense, because they cannot corrupt memory. [27]

## Stability: releases and editions

Rust 1.0 shipped on 15 May 2015, and from that point breaking changes were "largely out of scope", with a new stable release every six weeks. [69] At the time of writing the current release is 1.99.1, published on 15 October 2026. [21]

When the language does need a breaking change, such as a new keyword, it goes into a new **edition**. [22] Each crate picks its edition in `Cargo.toml`, crates of different editions work together in one program, and Cargo can migrate code automatically. [22] The editions are 2015, 2018, 2021 and 2024; Rust 2024 became stable in Rust 1.85.0. [22] [21] This course uses the 2024 edition.

:::low-confidence
No next edition had been accepted when this course was written; there is forum discussion of a 2027 edition and a draft proposal to stop tying editions to a fixed three-year rhythm. Check the Rust blog before relying on a date. [73]
:::

Rust is also used where certification matters: in 2025 the Rust Project adopted the FLS, a description of the language written by Ferrous Systems and AdaCore that had already been used to qualify Rust toolchains for safety-critical industries. [68]

:::key-takeaways
- Rust targets the memory bugs that dominate security fixes in C and C++ code bases, without a garbage collector.
- Safe Rust cannot cause undefined behavior; `unsafe` marks the small parts the compiler cannot check.
- Stable Rust ships every six weeks without breaking your code; breaking changes go into opt-in editions.
:::

:::glossary
- **Ownership**: Rust's rule that each value has one owner, which frees it when it goes away.
- **Borrow**: using a value through a reference without taking it over.
- **Borrow checker**: the part of the compiler that checks every borrow is valid.
- **Undefined behavior / UB**: an operation the language gives no meaning to, after which the program may do anything.
- **CVE**: a public identifier given to a known security vulnerability.
- **Edition**: a named, opt-in set of language changes, chosen per crate.
- **Crate**: one library or program that the compiler builds as a unit.
- **Cargo**: Rust's build tool and package manager.
- **Unsafe Rust**: Rust code inside `unsafe`, where some checks become the programmer's job.
:::
