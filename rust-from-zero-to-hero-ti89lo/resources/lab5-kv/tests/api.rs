// Tests call the router in-process: no network, no open port.
use axum::body::Body;
use axum::http::{Request, StatusCode};
use http_body_util::BodyExt;
use kv::{Db, app};
use tower::ServiceExt; // for `oneshot`

async fn send(db: &Db, method: &str, uri: &str, body: &str) -> (StatusCode, String) {
    let request = Request::builder()
        .method(method)
        .uri(uri)
        .body(Body::from(body.to_string()))
        .unwrap();
    let response = app(db.clone()).oneshot(request).await.unwrap();
    let status = response.status();
    let bytes = response.into_body().collect().await.unwrap().to_bytes();
    (status, String::from_utf8(bytes.to_vec()).unwrap())
}

#[tokio::test]
async fn put_get_delete() {
    let db = Db::default();
    assert_eq!(send(&db, "GET", "/kv/lang", "").await.0, StatusCode::NOT_FOUND);
    assert_eq!(send(&db, "PUT", "/kv/lang", "rust").await.0, StatusCode::CREATED);
    assert_eq!(send(&db, "PUT", "/kv/lang", "Rust").await.0, StatusCode::OK);
    assert_eq!(send(&db, "GET", "/kv/lang", "").await, (StatusCode::OK, "Rust".to_string()));
    assert_eq!(send(&db, "DELETE", "/kv/lang", "").await.0, StatusCode::NO_CONTENT);
    assert_eq!(send(&db, "DELETE", "/kv/lang", "").await.0, StatusCode::NOT_FOUND);
}

#[tokio::test]
async fn lists_keys_sorted() {
    let db = Db::default();
    for key in ["b", "a", "c"] {
        send(&db, "PUT", &format!("/kv/{key}"), "x").await;
    }
    let (status, body) = send(&db, "GET", "/kv", "").await;
    assert_eq!(status, StatusCode::OK);
    let json: serde_json::Value = serde_json::from_str(&body).unwrap();
    assert_eq!(json, serde_json::json!({ "keys": ["a", "b", "c"] }));
}

#[tokio::test]
async fn many_concurrent_writers() {
    let db = Db::default();
    let mut handles = Vec::new();
    for i in 0..100 {
        let db = db.clone();
        handles.push(tokio::spawn(async move {
            send(&db, "PUT", &format!("/kv/k{i}"), "v").await.0
        }));
    }
    for h in handles {
        assert_eq!(h.await.unwrap(), StatusCode::CREATED);
    }
    assert_eq!(db.read().unwrap().len(), 100);
}
