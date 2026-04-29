# Threading

```cpp
// Thread safety with shared state
use actix_web::{web, App, HttpServer, HttpResponse};
use std::sync::Arc;
use tokio::sync::RwLock;

struct SharedState {
    counter: RwLock<u64>,
    config: RwLock<String>,
}

async fn increment(state: web::Data<SharedState>) -> HttpResponse {
    let mut counter = state.counter.write().await;
    *counter += 1;
    HttpResponse::Ok().body(format!("Counter: {}", *counter))
}

async fn read_config(state: web::Data<SharedState>) -> HttpResponse {
    let config = state.config.read().await;
    HttpResponse::Ok().body(config.clone())
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let state = web::Data::new(SharedState {
        counter: RwLock::new(0),
        config: RwLock::new("production".to_string()),
    });
    
    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .route("/increment", web::post().to(increment))
            .route("/config", web::get().to(read_config))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// Thread-safe connection pool sharing
use actix_web::{web, App, HttpServer, HttpResponse};
use deadpool_postgres::{Config, Pool, Runtime};
use tokio_postgres::NoTls;
use std::sync::Arc;

struct DbPool {
    pool: Pool,
}

impl DbPool {
    fn new() -> Self {
        let mut cfg = Config::new();
        cfg.host = Some("localhost".to_string());
        cfg.port = Some(5432);
        cfg.dbname = Some("mydb".to_string());
        cfg.user = Some("user".to_string());
        cfg.password = Some("password".to_string());
        
        let pool = cfg.create_pool(Some(Runtime::Tokio1), NoTls).unwrap();
        DbPool { pool }
    }
}

// Thread-safe because Pool is Send + Sync
unsafe impl Send for DbPool {}
unsafe impl Sync for DbPool {}

async fn handler(pool: web::Data<DbPool>) -> HttpResponse {
    let client = pool.pool.get().await.unwrap();
    HttpResponse::Ok().body("Got connection from pool")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let pool = web::Data::new(DbPool::new());
    
    HttpServer::new(move || {
        App::new()
            .app_data(pool.clone())
            .route("/db", web::get().to(handler))
    })
    .workers(4) // 4 threads sharing the same pool
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// Concurrent access patterns with actor-based state
use actix_web::{web, App, HttpServer, HttpResponse};
use actix::prelude::*;

struct CounterActor {
    count: u64,
}

impl Actor for CounterActor {
    type Context = Context<Self>;
}

struct Increment;
struct GetCount;

impl Message for Increment {
    type Result = u64;
}

impl Message for GetCount {
    type Result = u64;
}

impl Handler<Increment> for CounterActor {
    type Result = u64;
    
    fn handle(&mut self, _msg: Increment, _ctx: &mut Context<Self>) -> u64 {
        self.count += 1;
        self.count
    }
}

impl Handler<GetCount> for CounterActor {
    type Result = u64;
    
    fn handle(&mut self, _msg: GetCount, _ctx: &mut Context<Self>) -> u64 {
        self.count
    }
}

async fn increment(counter: web::Data<Addr<CounterActor>>) -> HttpResponse {
    let count = counter.send(Increment).await.unwrap();
    HttpResponse::Ok().body(format!("Count: {}", count))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let counter = CounterActor { count: 0 }.start();
    let counter = web::Data::new(counter);
    
    HttpServer::new(move || {
        App::new()
            .app_data(counter.clone())
            .route("/increment", web::post().to(increment))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// Thread-safe caching with concurrent access
use actix_web::{web, App, HttpServer, HttpResponse};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use std::time::{Duration, Instant};

struct CacheEntry {
    value: String,
    expires_at: Instant,
}

struct ThreadSafeCache {
    cache: RwLock<HashMap<String, CacheEntry>>,
}

impl ThreadSafeCache {
    fn new() -> Self {
        ThreadSafeCache {
            cache: RwLock::new(HashMap::new()),
        }
    }
    
    async fn get(&self, key: &str) -> Option<String> {
        let cache = self.cache.read().await;
        if let Some(entry) = cache.get(key) {
            if Instant::now() < entry.expires_at {
                return Some(entry.value.clone());
            }
        }
        None
    }
    
    async fn set(&self, key: String, value: String, ttl: Duration) {
        let mut cache = self.cache.write().await;
        cache.insert(key, CacheEntry {
            value,
            expires_at: Instant::now() + ttl,
        });
    }
}

async fn handler(cache: web::Data<ThreadSafeCache>) -> HttpResponse {
    if let Some(cached) = cache.get("data").await {
        return HttpResponse::Ok().body(cached);
    }
    
    // Compute expensive operation
    let result = "expensive computation".to_string();
    cache.set("data".to_string(), result.clone(), Duration::from_secs(60)).await;
    HttpResponse::Ok().body(result)
}
```