use std::path::Path;
use std::time::Instant;
use std::{env, process, thread};

fn main() {
    let dir = env::args().nth(1).unwrap_or_else(|| "data".to_string());
    let threads = thread::available_parallelism().map(|n| n.get()).unwrap_or(4);

    let files = checksums::list_files(Path::new(&dir)).unwrap_or_else(|e| {
        eprintln!("cannot list {dir}: {e} (run `cargo run --release --bin gen` first)");
        process::exit(1);
    });
    println!("{} files in {dir}", files.len());

    let t = Instant::now();
    let seq = checksums::sequential(&files).expect("sequential run");
    let seq_time = t.elapsed();

    let t = Instant::now();
    let par = checksums::parallel(&files, threads).expect("parallel run");
    let par_time = t.elapsed();

    assert_eq!(seq, par, "both runs must agree");
    let combined = seq.iter().fold(0u64, |acc, (_, sum)| acc ^ sum);
    println!("combined checksum: {combined:016x}");
    println!("1 thread:  {seq_time:?}");
    println!("{threads} threads: {par_time:?}");
}
