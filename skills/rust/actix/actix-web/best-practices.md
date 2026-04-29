# Best Practices

```cpp
// Use structured logging with request IDs
use actix_web::{web, App, HttpServer, HttpResponse, middleware};
use uuid::Uuid;
use std::sync::atomic::{AtomicU64, Ordering};

struct RequestIdMiddleware;

impl<S, B> middleware::Transform<S, B> for RequestIdMiddleware
where
    S: middleware::Service<B>,
    B: 'static,
{
    type Response = S::Response;
    type Error = S::Error;
    type Transform = RequestIdService<S>;
    type InitError = ();
    type Future = Ready<Result<Self::Transform, Self::InitError>>;

    fn new_transform(&self, service: S) -> Self::Future {
        ok(RequestIdService { service })
    }
}

struct RequestIdService<S> {
    service: S,
}

impl<S, B> middleware::Service<B> for RequestIdService<S>
where
    S: middleware::Service<B>,
{
    type Response = S::Response;
    type Error = S::Error;
    type Future = S::Future;

    fn poll_ready(&self, cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        self.service.poll_ready(cx)
    }

    fn call(&self, req: B) -> Self::Future {
        let request_id = Uuid::new_v4().to_string();
        log::info!("Request {} started", request_id);
        self.service.call(req)
    }
}
```

```cpp
// Implement proper health checks
use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use serde::Serialize;

#[derive(Serialize)]
struct HealthResponse {
    status: String,
    version: String,
    uptime: u64,
}

async fn health_check() -> impl Responder {
    HttpResponse::Ok().json(HealthResponse {
        status: "healthy".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        uptime: std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs(),
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/health", web::get().to(health_check))
            .route("/api/v1/users", web::get().to(get_users))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// Use environment-based configuration
use actix_web::{web, App, HttpServer, HttpResponse};
use std::env;

struct Config {
    database_url: String,
    redis_url: String,
    log_level: String,
}

impl Config {
    fn from_env() -> Self {
        Config {
            database_url: env::var("DATABASE_URL")
                .expect("DATABASE_URL must be set"),
            redis_url: env::var("REDIS_URL")
                .unwrap_or_else(|_| "redis://localhost:6379".to_string()),
            log_level: env::var("LOG_LEVEL")
                .unwrap_or_else(|_| "info".to_string()),
        }
    }
}

async fn handler(config: web::Data<Config>) -> HttpResponse {
    HttpResponse::Ok().body(format!("Using database: {}", config.database_url))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let config = web::Data::new(Config::from_env());
    HttpServer::new(move || {
        App::new()
            .app_data(config.clone())
            .route("/config", web::get().to(handler))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// Implement rate limiting
use actix_web::{web, App, HttpServer, HttpResponse, middleware};
use std::collections::HashMap;
use std::sync::Mutex;
use std::time::{Duration, Instant};

struct RateLimiter {
    requests: Mutex<HashMap<String, Vec<Instant>>>,
    max_requests: usize,
    window: Duration,
}

impl RateLimiter {
    fn new(max_requests: usize, window_secs: u64) -> Self {
        RateLimiter {
            requests: Mutex::new(HashMap::new()),
            max_requests,
            window: Duration::from_secs(window_secs),
        }
    }

    fn check(&self, client_ip: &str) -> bool {
        let mut requests = self.requests.lock().unwrap();
        let now = Instant::now();
        let timestamps = requests.entry(client_ip.to_string()).or_insert_with(Vec::new);
        
        timestamps.retain(|&t| now - t < self.window);
        
        if timestamps.len() >= self.max_requests {
            false
        } else {
            timestamps.push(now);
            true
        }
    }
}
```