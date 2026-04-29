# Lifecycle

```cpp
// Construction: Creating the server with proper initialization
use actix_web::{web, App, HttpServer, HttpResponse};
use std::sync::Arc;

struct DatabasePool {
    connections: Vec<String>,
}

impl DatabasePool {
    fn new(size: usize) -> Self {
        let mut connections = Vec::with_capacity(size);
        for i in 0..size {
            connections.push(format!("connection_{}", i));
        }
        DatabasePool { connections }
    }
}

async fn handler(pool: web::Data<DatabasePool>) -> HttpResponse {
    HttpResponse::Ok().body(format!("Pool size: {}", pool.connections.len()))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let pool = web::Data::new(DatabasePool::new(10));
    
    HttpServer::new(move || {
        App::new()
            .app_data(pool.clone())
            .route("/", web::get().to(handler))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// Destruction: Proper cleanup on shutdown
use actix_web::{web, App, HttpServer, HttpResponse};
use tokio::sync::oneshot;

async fn handler() -> HttpResponse {
    HttpResponse::Ok().body("Hello")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let (tx, rx) = oneshot::channel();
    
    let server = HttpServer::new(|| {
        App::new().route("/", web::get().to(handler))
    })
    .bind("127.0.0.1:8080")?
    .run();
    
    // Handle shutdown signal
    tokio::spawn(async move {
        tokio::signal::ctrl_c().await.unwrap();
        tx.send(()).unwrap();
    });
    
    rx.await.unwrap();
    server.stop(true).await; // Graceful shutdown
    Ok(())
}
```

```cpp
// Move semantics: Cloning shared state correctly
use actix_web::{web, App, HttpServer, HttpResponse};
use std::sync::Arc;

struct AppConfig {
    database_url: String,
    api_key: String,
}

async fn handler(config: web::Data<AppConfig>) -> HttpResponse {
    HttpResponse::Ok().body(format!("Config: {}", config.database_url))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let config = web::Data::new(AppConfig {
        database_url: "postgres://localhost/mydb".to_string(),
        api_key: "secret".to_string(),
    });
    
    // Clone the Data handle (not the inner config) for each worker
    HttpServer::new(move || {
        App::new()
            .app_data(config.clone()) // Clones Arc, not AppConfig
            .route("/", web::get().to(handler))
    })
    .workers(4) // 4 workers sharing the same config
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// Resource management: Connection pooling and cleanup
use actix_web::{web, App, HttpServer, HttpResponse};
use deadpool_postgres::{Config, Pool, Runtime};
use tokio_postgres::NoTls;

struct DbPool {
    pool: Pool,
}

impl DbPool {
    async fn new() -> Self {
        let mut cfg = Config::new();
        cfg.host = Some("localhost".to_string());
        cfg.port = Some(5432);
        cfg.dbname = Some("mydb".to_string());
        cfg.user = Some("user".to_string());
        cfg.password = Some("password".to_string());
        
        let pool = cfg.create_pool(Some(Runtime::Tokio1), NoTls).unwrap();
        DbPool { pool }
    }
    
    async fn get_connection(&self) -> Result<deadpool_postgres::Client, actix_web::Error> {
        self.pool.get().await.map_err(|e| {
            actix_web::error::ErrorInternalServerError(format!("DB error: {}", e))
        })
    }
}

async fn handler(pool: web::Data<DbPool>) -> HttpResponse {
    let client = pool.get_connection().await.unwrap();
    HttpResponse::Ok().body("Connected to database")
}
```