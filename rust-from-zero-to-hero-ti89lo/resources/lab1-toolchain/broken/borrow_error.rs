// Does not compile on purpose. Try: rustc --edition 2024 broken/borrow_error.rs
fn main() {
    let mut numbers = vec![1, 2, 3];
    let first = &numbers[0]; // shared borrow of `numbers`
    numbers.push(10); // error: mutable borrow while `first` is still used
    println!("first = {first}");
}
