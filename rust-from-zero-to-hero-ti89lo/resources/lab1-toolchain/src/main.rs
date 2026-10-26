// Lab 1: the fixed versions of the three programs in `broken/`.
// Run with `cargo run`. Each function shows the fix for one compiler error.

fn fixed_move() -> String {
    let greeting = String::from("hello");
    // Fix: borrow instead of moving, so `greeting` stays usable.
    let borrowed = &greeting;
    format!("{borrowed}, {greeting}")
}

fn fixed_borrow() -> Vec<i32> {
    let mut numbers = vec![1, 2, 3];
    // Fix: read what we need, let the shared borrow end, then mutate.
    let first = numbers[0];
    numbers.push(first * 10);
    numbers
}

fn fixed_types() -> u32 {
    let text = "42";
    // Fix: tell `parse` which type we want, and handle the error case.
    let n: u32 = text.parse().expect("text should be a number");
    n + 1
}

fn main() {
    println!("move:   {}", fixed_move());
    println!("borrow: {:?}", fixed_borrow());
    println!("types:  {}", fixed_types());
}
