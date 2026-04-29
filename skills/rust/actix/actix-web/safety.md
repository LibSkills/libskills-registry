# Safety

```cpp
// RED LINE 1: Never expose internal error details to clients
// BAD: Leaking stack traces
use actix_web::{web, App, HttpServer, HttpResponse, error};

async fn bad_handler() -> HttpResponse {
    let result = std::fs::read_to_string("/etc/passwd");
    match result {
        Ok(content) => HttpResponse::Ok().body(content),
        Err(e) => HttpResponse::InternalServerError().body(format!("Error: {:?}", e)), // Leaks internal details
    }
}

// GOOD: Generic error messages
use actix_web::{web, App, HttpServer, HttpResponse, error};

async fn good_handler() -> Result<HttpResponse, actix_web::Error> {
    let result = std::fs::read_to_string("/etc/passwd")
        .map_err(|_| actix_web::error::ErrorInternalServerError("Internal server error"))?;
    Ok(HttpResponse::Ok().body(result))
}
```

```cpp
// RED LINE 2: Never use unwrap() or expect() in production handlers
// BAD: Panic on error
use actix_web::{web, App, HttpServer, HttpResponse};

async fn bad_handler() -> HttpResponse {
    let data = some_fallible_operation().unwrap(); // Crashes the worker
    HttpResponse::Ok().body(data)
}

// GOOD: Handle errors gracefully
use actix_web::{web, App, HttpServer, HttpResponse, error};

async fn good_handler() -> Result<HttpResponse, actix_web::Error> {
    let data = some_fallible_operation()
        .map_err(|e| actix_web::error::ErrorBadRequest(e))?;
    Ok(HttpResponse::Ok().body(data))
}
```

```cpp
// RED LINE 3: Never allow unbounded request bodies
// BAD: No size limit
use actix_web::{web, App, HttpServer, HttpResponse};

async fn bad_handler(body: web::Bytes) -> HttpResponse {
    HttpResponse::Ok().body(format!("Received {} bytes", body.len()))
}

// GOOD: Limit payload size
use actix_web::{web, App, HttpServer, HttpResponse, middleware};

async fn good_handler(body: web::Bytes) -> HttpResponse {
    HttpResponse::Ok().body(format!("Received {} bytes", body.len()))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .app_data(web::JsonConfig::default().limit(4096)) // 4KB limit
            .route("/", web::post().to(good_handler))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// RED LINE 4: Never use mutable global state without synchronization
// BAD: Unsynchronized mutable state
use actix_web::{web, App, HttpServer, HttpResponse};
use std::sync::Mutex;

static mut COUNTER: u32 = 0; // Unsafe mutable static

async fn bad_handler() -> HttpResponse {
    unsafe { COUNTER += 1; } // Data race
    HttpResponse::Ok().body("Incremented")
}

// GOOD: Proper synchronization
use actix_web::{web, App, HttpServer, HttpResponse};
use std::sync::Mutex;

struct AppState {
    counter: Mutex<u32>,
}

async fn good_handler(data: web::Data<AppState>) -> HttpResponse {
    let mut counter = data.counter.lock().unwrap();
    *counter += 1;
    HttpResponse::Ok().body("Incremented")
}
```

```cpp
// RED LINE 5: Never ignore TLS/SSL configuration in production
// BAD: No TLS in production
use actix_web::{web, App, HttpServer, HttpResponse};

async fn handler() -> HttpResponse {
    HttpResponse::Ok().body("Sensitive data")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| App::new().route("/", web::get().to(handler)))
        .bind("0.0.0.0:443")? // Exposed without TLS
        .run()
        .await
}

// GOOD: Proper TLS configuration
use actix_web::{web, App, HttpServer, HttpResponse};
use openssl::ssl::{SslAcceptor, SslFiletype, SslMethod};

async fn handler() -> HttpResponse {
    HttpResponse::Ok().body("Sensitive data")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let mut builder = SslAcceptor::mozilla_intermediate(SslMethod::tls()).unwrap();
    builder.set_private_key_file("key.pem", SslFiletype::PEM).unwrap();
    builder.set_certificate_chain_file("cert.pem").unwrap();

    HttpServer::new(|| App::new().route("/", web::get().to(handler)))
        .bind_openssl("0.0.0.0:443", builder)?
        .run()
        .await
}
```