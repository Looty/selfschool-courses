use std::{env, fs, process};

fn main() {
    let mut args = env::args().skip(1);
    let Some(path) = args.next() else {
        eprintln!("usage: wordfreq <file> [top-n]");
        process::exit(2);
    };
    let n: usize = match args.next() {
        Some(s) => s.parse().unwrap_or_else(|_| {
            eprintln!("top-n must be a whole number, got {s:?}");
            process::exit(2);
        }),
        None => 5,
    };
    let text = fs::read_to_string(&path).unwrap_or_else(|e| {
        eprintln!("cannot read {path}: {e}");
        process::exit(1);
    });

    let counts = wordfreq::count_words(&text);
    let total: usize = counts.values().sum();
    println!("{total} words, {} distinct", counts.len());
    for (word, count) in wordfreq::top_n(&counts, n) {
        println!("{count:>5}  {word}");
    }
}
