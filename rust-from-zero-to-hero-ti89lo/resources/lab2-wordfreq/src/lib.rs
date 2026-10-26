//! Word frequency counting with iterators and a HashMap.

use std::collections::HashMap;

/// Splits `text` into lowercase words. A word is a run of alphanumeric
/// characters or apostrophes; everything else separates words.
pub fn words(text: &str) -> impl Iterator<Item = String> + '_ {
    text.split(|c: char| !(c.is_alphanumeric() || c == '\''))
        .map(|w| w.trim_matches('\''))
        .filter(|w| !w.is_empty())
        .map(str::to_lowercase)
}

/// Counts how often each word occurs.
pub fn count_words(text: &str) -> HashMap<String, usize> {
    let mut counts = HashMap::new();
    for word in words(text) {
        *counts.entry(word).or_insert(0) += 1;
    }
    counts
}

/// Returns the `n` most frequent words, most frequent first.
/// Ties are broken alphabetically so the output is deterministic.
pub fn top_n(counts: &HashMap<String, usize>, n: usize) -> Vec<(&str, usize)> {
    let mut pairs: Vec<(&str, usize)> = counts.iter().map(|(w, &c)| (w.as_str(), c)).collect();
    pairs.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(b.0)));
    pairs.truncate(n);
    pairs
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn splits_and_lowercases() {
        let w: Vec<String> = words("Hello, hello WORLD!").collect();
        assert_eq!(w, ["hello", "hello", "world"]);
    }

    #[test]
    fn keeps_apostrophes_inside_words() {
        let w: Vec<String> = words("don't 'quote'").collect();
        assert_eq!(w, ["don't", "quote"]);
    }

    #[test]
    fn counts_words() {
        let c = count_words("a b a c a b");
        assert_eq!(c["a"], 3);
        assert_eq!(c["b"], 2);
        assert_eq!(c.get("z"), None);
    }

    #[test]
    fn top_n_breaks_ties_alphabetically() {
        let c = count_words("pear apple pear apple fig");
        assert_eq!(top_n(&c, 2), [("apple", 2), ("pear", 2)]);
    }

    #[test]
    fn empty_text_has_no_words() {
        assert!(count_words("  ...  ").is_empty());
    }
}
