//! Checksums of many files, computed on one thread or several.

use std::path::{Path, PathBuf};
use std::sync::mpsc;
use std::{fs, io, thread};

/// FNV-1a, a simple 64-bit hash. Good enough to compare runs; not cryptographic.
pub fn fnv1a(bytes: &[u8]) -> u64 {
    let mut hash: u64 = 0xcbf2_9ce4_8422_2325;
    for &b in bytes {
        hash ^= u64::from(b);
        hash = hash.wrapping_mul(0x0000_0100_0000_01b3);
    }
    hash
}

/// All regular files directly inside `dir`, sorted by name.
pub fn list_files(dir: &Path) -> io::Result<Vec<PathBuf>> {
    let mut files = Vec::new();
    for entry in fs::read_dir(dir)? {
        let path = entry?.path();
        if path.is_file() {
            files.push(path);
        }
    }
    files.sort();
    Ok(files)
}

fn checksum_file(path: &Path) -> io::Result<u64> {
    Ok(fnv1a(&fs::read(path)?))
}

/// One thread: hash the files one after another.
pub fn sequential(files: &[PathBuf]) -> io::Result<Vec<(PathBuf, u64)>> {
    files.iter().map(|p| Ok((p.clone(), checksum_file(p)?))).collect()
}

/// Several threads: split the file list into `threads` chunks. Each scoped
/// thread borrows its chunk (no cloning of the list) and sends results back
/// over a channel. The scope joins every thread before it returns.
pub fn parallel(files: &[PathBuf], threads: usize) -> io::Result<Vec<(PathBuf, u64)>> {
    let threads = threads.max(1);
    let chunk_size = files.len().div_ceil(threads).max(1);
    let (tx, rx) = mpsc::channel();

    thread::scope(|s| {
        for chunk in files.chunks(chunk_size) {
            let tx = tx.clone();
            s.spawn(move || {
                for path in chunk {
                    let result = checksum_file(path).map(|sum| (path.clone(), sum));
                    // The receiver lives until after the scope, so send cannot fail.
                    tx.send(result).expect("receiver alive");
                }
            });
        }
    });
    drop(tx); // close the channel so the iterator below ends

    let mut results = rx.into_iter().collect::<io::Result<Vec<_>>>()?;
    results.sort();
    Ok(results)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fnv1a_known_values() {
        // Reference values of 64-bit FNV-1a.
        assert_eq!(fnv1a(b""), 0xcbf2_9ce4_8422_2325);
        assert_eq!(fnv1a(b"a"), 0xaf63_dc4c_8601_ec8c);
    }

    #[test]
    fn parallel_matches_sequential() {
        let dir = std::env::temp_dir().join("checksums-test");
        let _ = fs::remove_dir_all(&dir);
        fs::create_dir_all(&dir).unwrap();
        for i in 0..7 {
            fs::write(dir.join(format!("f{i}.bin")), vec![i as u8; 1000 + i]).unwrap();
        }
        let files = list_files(&dir).unwrap();
        let a = sequential(&files).unwrap();
        for threads in [1, 2, 3, 8] {
            assert_eq!(parallel(&files, threads).unwrap(), a, "threads = {threads}");
        }
        fs::remove_dir_all(&dir).unwrap();
    }
}
