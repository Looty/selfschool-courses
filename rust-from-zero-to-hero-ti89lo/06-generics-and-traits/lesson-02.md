---
id: l15
title: Traits and trait bounds
quiz: quiz-15.yaml
sources: [9, 12, 19, 20, 66]
---
After this lesson you can define and implement traits, use default methods, write bounds with `impl Trait`, `+` and `where`, and explain the orphan rule.

## Defining and implementing a trait

A trait is a set of method signatures that types can implement; it is close to what other languages call an interface. [9]

```rust
pub trait Summary {
    fn summarize_author(&self) -> String;          // required
    fn summarize(&self) -> String {                // default method
        format!("(Read more from {}...)", self.summarize_author())
    }
}

pub struct Post { pub username: String, pub content: String }

impl Summary for Post {
    fn summarize_author(&self) -> String { format!("@{}", self.username) }
}
```

A default method can call required methods, so implementors write a little and get a lot; an implementation can still override any default. [9] To call trait methods, the trait must be in scope (`use crate::Summary;`). [9]

## The orphan rule

You may implement a trait for a type only if the trait or the type (or both) is defined in your crate. [9] You can implement your `Summary` for `Vec<T>`, or the standard `Display` for your `Post`, but not `Display` for `Vec<T>`. [9] This rule, part of *coherence*, guarantees that two crates can never provide conflicting implementations of the same trait for the same type. [9] The usual workaround is a **newtype**, a one-field tuple struct such as `struct Wrapper(Vec<String>);`, which is local and costs nothing at run time. [19]

## Traits as bounds

```rust
// impl Trait in argument position: any type implementing Summary
pub fn notify(item: &impl Summary) { println!("Breaking: {}", item.summarize()); }

// the same, written as a trait bound
pub fn notify2<T: Summary>(item: &T) { println!("Breaking: {}", item.summarize()); }

// several bounds, and a where clause for readability
fn report<T, U>(t: &T, u: &U) -> String
where
    T: Summary + std::fmt::Display,
    U: Clone + std::fmt::Debug,
{
    format!("{t} {u:?} {}", t.summarize())
}
```

`impl Trait` is shorthand for a generic bound; use the explicit `<T: Summary>` form when two parameters must be the **same** type, since two `impl Summary` parameters may differ. [9] `+` combines bounds and `where` moves long bound lists after the signature. [9]

`impl Trait` can also appear in return position, meaning "some type implementing this trait" without naming it. That is how functions return closures and iterators, whose types are unnameable or very long. [9] [12] It must still be one concrete type: a function cannot return a `Post` on one branch and another type on another under `-> impl Summary`. [9]

## Conditional and blanket implementations

```rust
impl<T: std::fmt::Display + PartialOrd> Pair<T> {
    fn cmp_display(&self) { /* only for T that can be compared and shown */ }
}
```

Bounds on an `impl` block add methods only for types that meet them. [9] A **blanket implementation** implements a trait for every type meeting a bound; the standard library has `impl<T: Display> ToString for T`, which is why `3.to_string()` works. [9]

## Derivable traits and associated types

`#[derive(...)]` generates standard implementations for `Debug`, `PartialEq`/`Eq`, `PartialOrd`/`Ord`, `Clone`/`Copy`, `Hash` and `Default`; `Display` cannot be derived because only you know how a value should look to users. [20] The API Guidelines ask public types to implement the common traits eagerly. [66]

Some traits have an **associated type**, a placeholder the implementor fills in once. `Iterator` declares `type Item;`, and each implementation says what `Item` is; unlike a generic parameter, this means a type can implement `Iterator` only once. [19] Operators are traits too: implementing `std::ops::Add` for your type makes `+` work on it. [19]

:::key-takeaways
- Traits define shared behavior; default methods reduce what implementors write.
- The orphan rule: you can implement a trait for a type only if one of them is yours; newtypes get around it.
- `impl Trait`, `T: Trait`, `+` and `where` express bounds; blanket impls cover every type that meets a bound.
:::

:::glossary
- **Trait**: a named set of methods that types can implement, like an interface.
- **Default method**: a trait method with a body that implementors get for free.
- **Orphan rule**: you may implement a trait for a type only if the trait or the type is local to your crate.
- **Coherence**: the guarantee that there is at most one implementation of a trait for a type.
- **Newtype**: a one-field wrapper struct used to create a distinct type.
- **impl Trait**: "some type that implements this trait", in a parameter or return type.
- **where clause**: a place after the signature to list trait bounds.
- **Blanket implementation**: implementing a trait for every type that meets a bound.
- **Associated type**: a type placeholder inside a trait, chosen by each implementation.
:::
