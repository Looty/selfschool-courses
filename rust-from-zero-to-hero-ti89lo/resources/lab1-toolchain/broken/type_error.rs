// Does not compile on purpose. Try: rustc --edition 2024 broken/type_error.rs
fn main() {
    let text = "42";
    let n = text.parse().unwrap(); // error: which type should `parse` produce?
    println!("{}", n + 1);
}
