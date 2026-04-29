# Quickstart

```cpp
// Basic Hello World
use actix_web::{web, App, HttpServer, Responder};

async fn hello() -> impl Responder {
    "Hello World!"
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/", web::get().to(hello))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// Path parameters
use actix_web::{get, web, App, HttpServer, Responder};

#[get("/users/{id}")]
async fn get_user(path: web::Path<u32>) -> impl Responder {
    format!("User ID: {}", path.into_inner())
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| App::new().service(get_user))
        .bind("127.0.0.1:8080")?
        .run()
        .await
}
```

```cpp
// JSON request/response
use actix_web::{web, App, HttpServer, Responder};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct User {
    name: String,
    age: u32,
}

async fn create_user(user: web::Json<User>) -> impl Responder {
    web::Json(User {
        name: user.name.clone(),
        age: user.age,
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/users", web::post().to(create_user))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// Shared application state
use actix_web::{web, App, HttpServer, Responder};
use std::sync::Mutex;

struct AppState {
    counter: Mutex<u32>,
}

async fn increment(data: web::Data<AppState>) -> impl Responder {
    let mut counter = data.counter.lock().unwrap();
    *counter += 1;
    format!("Counter: {}", *counter)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let data = web::Data::new(AppState {
        counter: Mutex::new(0),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .route("/increment", web::get().to(increment))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// Middleware (logging)
use actix_web::{middleware, web, App, HttpServer, Responder};

async fn index() -> impl Responder {
    "Hello with logging!"
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .wrap(middleware::Logger::default())
            .route("/", web::get().to(index))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// Error handling with custom error type
use actix_web::{web, App, HttpServer, Responder, HttpResponse, error};
use thiserror::Error;

#[derive(Error, Debug)]
enum MyError {
    #[error("Not found")]
    NotFound,
    #[error("Internal error: {0}")]
    Internal(String),
}

impl error::ResponseError for MyError {
    fn error_response(&self) -> HttpResponse {
        match self {
            MyError::NotFound => HttpResponse::NotFound().finish(),
            MyError::Internal(msg) => HttpResponse::InternalServerError().body(msg.clone()),
        }
    }
}

async fn fail() -> Result<&'static str, MyError> {
    Err(MyError::NotFound)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| App::new().route("/fail", web::get().to(fail)))
        .bind("127.0.0.1:8080")?
        .run()
        .await
}
```