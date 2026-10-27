---
id: l14
title: Generics and monomorphization
quiz: quiz-14.yaml
sources: [9, 19]
---
After this lesson you can write generic functions, structs, enums and methods, and explain why generics in Rust cost nothing at run time.

## Generic functions

```rust
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}

let n = largest(&[34, 50, 25, 100, 65]);   // &i32 -> 100
let c = largest(&['y', 'm', 'a', 'q']);    // &char -> 'y'
```

Type parameters are declared in angle brackets after the name, usually as short UpperCamelCase names such as `T`. [9] Without the `: PartialOrd` part, this does not compile: the body uses `>`, and the compiler will not assume every possible `T` can be compared. [9] That `T: PartialOrd` is a **trait bound**, the subject of the next lesson: the body may only use what the bounds promise. [9] If you know C++ templates, this is the main difference to keep in mind: the generic body is checked against its declared bounds, not just against the types it happens to be used with.

## Generic structs and enums

```rust
struct Point<T> { x: T, y: T }          // x and y share one type
struct Pair<T, U> { a: T, b: U }        // two independent types

enum Option<T> { Some(T), None }        // the standard library's own definitions
enum Result<T, E> { Ok(T), Err(E) }
```

`Point { x: 5, y: 4.0 }` does not compile, because `T` cannot be both an integer and a float; use two parameters when the fields may differ. [9] Many parameters make code hard to read, which often means it should be split up. [9]

## Generic methods, and methods for one type

```rust
impl<T> Point<T> {
    fn x(&self) -> &T { &self.x }               // for every Point<T>
}

impl Point<f32> {
    fn distance_from_origin(&self) -> f32 {     // only for Point<f32>
        (self.x.powi(2) + self.y.powi(2)).sqrt()
    }
}
```

`impl<T>` declares `T` so that `Point<T>` refers to the generic type; an `impl Point<f32>` without parameters adds methods to one concrete type only. [9] Methods can also introduce their own type parameters in addition to the struct's. [9]

## Monomorphization: zero runtime cost

The compiler generates a separate, specialized copy of generic code for each concrete type it is used with. [9] For `Some(5)` and `Some(5.0)` it effectively produces an `Option_i32` and an `Option_f64`. [9] This **monomorphization** means generic code runs exactly as fast as code you duplicated by hand. [9] The trade-off is more machine code when a generic is used with many types; trait objects, in lesson 3 of this chapter, trade the other way.

## A note on sizes

By default every type parameter has an implicit `T: Sized` bound: generic functions only accept types whose size is known at compile time. [19] Writing `T: ?Sized` relaxes that, so the function can accept unsized types such as `str` or `[u8]`, which must then be used behind a pointer like `&T`. [19]

```rust
fn show<T: std::fmt::Display + ?Sized>(t: &T) { println!("{t}"); }
show("text");   // T = str
```

:::key-takeaways
- Generics take type parameters in `<>`; bounds like `T: PartialOrd` say what the body may do with `T`.
- `impl<T> Type<T>` is for every `T`; `impl Type<f32>` is for one concrete type.
- Monomorphization copies generic code per type: no runtime cost, some extra code size.
:::

:::glossary
- **Generic**: code written once for many types, using type parameters.
- **Type parameter**: a placeholder type name such as `T`.
- **Trait bound**: a requirement such as `T: PartialOrd` that a type parameter must meet.
- **Monomorphization**: generating one specialized copy of generic code per concrete type.
- **PartialOrd**: the trait that provides `<`, `>`, `<=` and `>=`.
- **Sized**: the trait for types whose size is known at compile time.
- **Unsized type**: a type such as `str` whose size is only known at run time.
- **UpperCamelCase**: naming with each word capitalized and no separators, as in `HashMap`.
:::
