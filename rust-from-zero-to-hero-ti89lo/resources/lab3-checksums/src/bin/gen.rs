//! Writes 64 files of 4 MiB pseudo-random bytes into `data/` (256 MiB total).
//! A fixed seed makes the bytes, and so the checksums, the same on every machine.
use std::fs;

fn main() -> std::io::Result<()> {
    const FILES: u64 = 64;
    const SIZE: usize = 4 * 1024 * 1024;
    fs::create_dir_all("data")?;
    let mut state: u64 = 42; // seed
    let mut buf = vec![0u8; SIZE];
    for i in 0..FILES {
        for b in buf.iter_mut() {
            // A linear congruential generator: fast, deterministic, not secure.
            state = state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
            *b = (state >> 56) as u8;
        }
        fs::write(format!("data/file{i:02}.bin"), &buf)?;
    }
    println!("wrote {FILES} files of {SIZE} bytes to data/");
    Ok(())
}
