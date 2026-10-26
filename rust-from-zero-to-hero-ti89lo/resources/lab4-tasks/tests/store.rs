// Integration tests: they use only the public API of the `tasks` library.
use std::fs;
use std::path::PathBuf;
use tasks::{Store, StoreError};

fn temp_file(name: &str) -> PathBuf {
    let path = std::env::temp_dir().join(format!("tasks-test-{name}.json"));
    let _ = fs::remove_file(&path);
    path
}

#[test]
fn missing_file_gives_empty_store() {
    let store = Store::load(&temp_file("missing")).unwrap();
    assert_eq!(store.list(true).count(), 0);
}

#[test]
fn add_complete_and_reload() {
    let path = temp_file("roundtrip");
    let mut store = Store::load(&path).unwrap();
    assert_eq!(store.add("write lab 4").unwrap().id, 1);
    assert_eq!(store.add("  test it  ").unwrap().title, "test it");
    store.complete(1).unwrap();
    store.save(&path).unwrap();

    let reloaded = Store::load(&path).unwrap();
    let open: Vec<_> = reloaded.list(false).map(|t| t.id).collect();
    assert_eq!(open, [2]);
    assert_eq!(reloaded.list(true).count(), 2);
    fs::remove_file(&path).unwrap();
}

#[test]
fn errors_are_typed() {
    let mut store = Store::default();
    assert!(matches!(store.add("   "), Err(StoreError::EmptyTitle)));
    assert!(matches!(store.complete(99), Err(StoreError::NotFound(99))));
    let err = store.remove(7).unwrap_err();
    assert_eq!(err.to_string(), "no task with id 7");
}

#[test]
fn corrupt_file_is_a_json_error() {
    let path = temp_file("corrupt");
    fs::write(&path, "not json").unwrap();
    assert!(matches!(Store::load(&path), Err(StoreError::Json(_))));
    fs::remove_file(&path).unwrap();
}
