# Pitfalls

```cpp
// BAD: Blocking the async runtime with synchronous I/O
use actix_web::{web, App, HttpServer, Responder};
use std::thread;
use std::time::Duration;

async fn bad_handler() -> impl Responder {
    thread::sleep(Duration::from_secs(5)); // Blocks the worker thread
    "Done"
}

// GOOD: Using async sleep
use actix_web::{web, App, HttpServer, Responder};
use tokio::time::{sleep, Duration};

async fn good_handler() -> impl Responder {
    sleep(Duration::from_secs(5)).await; // Non-blocking
    "Done"
}
```

```cpp
// BAD: Using unwrap() in async handlers
use actix_web::{web, App, HttpServer, Responder, HttpResponse};

async fn bad_handler() -> HttpResponse {
    let result = some_fallible_operation().unwrap(); // Panics on error
    HttpResponse::Ok().body(result)
}

// GOOD: Proper error propagation
use actix_web::{web, App, HttpServer, Responder, HttpResponse, error};

async fn good_handler() -> Result<HttpResponse, actix_web::Error> {
    let result = some_fallible_operation().map_err(|e| {
        actix_web::error::ErrorInternalServerError(e)
    })?;
    Ok(HttpResponse::Ok().body(result))
}
```

```cpp
// BAD: Creating large state objects inside the closure
use actix_web::{web, App, HttpServer, Responder};
use std::collections::HashMap;

async fn bad_handler(data: web::Data<HashMap<String, String>>) -> impl Responder {
    format!("Data size: {}", data.len())
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        let large_map = HashMap::new(); // Recreated for each worker
        App::new().app_data(web::Data::new(large_map))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}

// GOOD: Sharing state across workers
use actix_web::{web, App, HttpServer, Responder};
use std::collections::HashMap;
use std::sync::Arc;

async fn good_handler(data: web::Data<HashMap<String, String>>) -> impl Responder {
    format!("Data size: {}", data.len())
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let shared_map = web::Data::new(HashMap::new()); // Created once
    HttpServer::new(move || {
        App::new().app_data(shared_map.clone())
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// BAD: Forgetting to handle CORS for cross-origin requests
use actix_web::{web, App, HttpServer, Responder};

async fn api_handler() -> impl Responder {
    "Sensitive data"
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new().route("/api/data", web::get().to(api_handler))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}

// GOOD: Adding CORS middleware
use actix_cors::Cors;
use actix_web::{web, App, HttpServer, Responder};

async fn api_handler() -> impl Responder {
    "Sensitive data"
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        let cors = Cors::default()
            .allowed_origin("https://trusted-site.com")
            .allowed_methods(vec!["GET", "POST"]);
        App::new()
            .wrap(cors)
            .route("/api/data", web::get().to(api_handler))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// BAD: Not using connection pooling for database
use actix_web::{web, App, HttpServer, Responder};
use sqlx::PgConnection;

async fn bad_handler() -> impl Responder {
    let conn = PgConnection::connect("postgres://...").await.unwrap(); // New connection per request
    // Use connection
    "Done"
}

// GOOD: Using connection pool
use actix_web::{web, App, HttpServer, Responder};
use sqlx::PgPool;

async fn good_handler(pool: web::Data<PgPool>) -> impl Responder {
    let row = sqlx::query("SELECT 1")
        .fetch_one(pool.get_ref())
        .await
        .unwrap();
    "Done"
}
```