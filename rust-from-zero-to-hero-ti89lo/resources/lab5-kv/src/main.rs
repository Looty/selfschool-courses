use kv::{Db, app};

#[tokio::main]
async fn main() {
    let db = Db::default();
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000")
        .await
        .expect("port 3000 should be free");
    println!("listening on http://{}", listener.local_addr().unwrap());

    axum::serve(listener, app(db))
        .with_graceful_shutdown(async {
            tokio::signal::ctrl_c().await.expect("install Ctrl+C handler");
            println!("shutting down");
        })
        .await
        .unwrap();
}
