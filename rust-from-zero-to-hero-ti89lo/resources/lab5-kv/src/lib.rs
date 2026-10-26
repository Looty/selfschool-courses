//! An in-memory key-value store behind an HTTP API.
//!
//!   GET    /kv          -> JSON list of keys
//!   GET    /kv/{key}    -> the value as text, or 404
//!   PUT    /kv/{key}    -> store the request body as the value (201 new, 200 replaced)
//!   DELETE /kv/{key}    -> 204, or 404

use axum::{
    Json, Router,
    extract::{Path, State},
    http::StatusCode,
    routing::get,
};
use serde::Serialize;
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

/// Shared state. axum clones it for every request, so it is an `Arc`:
/// cloning only bumps a reference count.
pub type Db = Arc<RwLock<HashMap<String, String>>>;

#[derive(Serialize)]
pub struct Keys {
    pub keys: Vec<String>,
}

pub fn app(db: Db) -> Router {
    Router::new()
        .route("/kv", get(list_keys))
        .route("/kv/{key}", get(get_value).put(put_value).delete(delete_value))
        .with_state(db)
}

// A std RwLock is fine here: every guard is dropped before the handler
// returns and no guard is held across an `.await`.

async fn list_keys(State(db): State<Db>) -> Json<Keys> {
    let mut keys: Vec<String> = db.read().unwrap().keys().cloned().collect();
    keys.sort();
    Json(Keys { keys })
}

async fn get_value(State(db): State<Db>, Path(key): Path<String>) -> Result<String, StatusCode> {
    db.read().unwrap().get(&key).cloned().ok_or(StatusCode::NOT_FOUND)
}

async fn put_value(State(db): State<Db>, Path(key): Path<String>, body: String) -> StatusCode {
    match db.write().unwrap().insert(key, body) {
        None => StatusCode::CREATED,
        Some(_old) => StatusCode::OK,
    }
}

async fn delete_value(State(db): State<Db>, Path(key): Path<String>) -> StatusCode {
    match db.write().unwrap().remove(&key) {
        Some(_) => StatusCode::NO_CONTENT,
        None => StatusCode::NOT_FOUND,
    }
}
