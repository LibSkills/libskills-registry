# Performance

```cpp
// Use streaming responses for large payloads
use actix_web::{web, App, HttpServer, HttpResponse, body::SizedStream};
use tokio::fs::File;
use tokio_util::io::ReaderStream;

async fn stream_file() -> HttpResponse {
    let file = File::open("large_file.dat").await.unwrap();
    let stream = ReaderStream::new(file);
    let stream = SizedStream::new(1024 * 1024 * 100, stream); // 100MB
    HttpResponse::Ok()
        .content_type("application/octet-stream")
        .streaming(stream)
}
```

```cpp
// Optimize JSON serialization with pre-allocated buffers
use actix_web::{web, App, HttpServer, HttpResponse};
use serde::Serialize;
use serde_json::Serializer;

#[derive(Serialize)]
struct LargeResponse {
    data: Vec<u32>,
    metadata: String,
}

async fn optimized_json() -> HttpResponse {
    let response = LargeResponse {
        data: (0..10000).collect(),
        metadata: "large dataset".to_string(),
    };
    
    // Pre-allocate buffer for better performance
    let mut buffer = Vec::with_capacity(1024 * 1024); // 1MB pre-allocation
    let mut serializer = Serializer::new(&mut buffer);
    response.serialize(&mut serializer).unwrap();
    
    HttpResponse::Ok()
        .content_type("application/json")
        .body(buffer)
}
```

```cpp
// Use connection pooling and keep-alive
use actix_web::{web, App, HttpServer, HttpResponse};
use actix_web::middleware::Compress;

async fn handler() -> HttpResponse {
    HttpResponse::Ok().body("Hello")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .wrap(Compress::default()) // Enable compression
            .route("/", web::get().to(handler))
    })
    .keep_alive(75) // Keep connections alive for 75 seconds
    .client_request_timeout(std::time::Duration::from_secs(30))
    .client_disconnect_timeout(std::time::Duration::from_secs(1))
    .workers(num_cpus::get()) // Use all CPU cores
    .backlog(1024) // Increase connection backlog
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
```

```cpp
// Minimize allocations with reusable buffers
use actix_web::{web, App, HttpServer, HttpResponse};
use bytes::BytesMut;
use std::sync::Arc;

struct BufferPool {
    buffers: Arc<tokio::sync::Mutex<Vec<BytesMut>>>,
}

impl BufferPool {
    fn new() -> Self {
        BufferPool {
            buffers: Arc::new(tokio::sync::Mutex::new(Vec::new())),
        }
    }
    
    async fn acquire(&self) -> BytesMut {
        let mut pool = self.buffers.lock().await;
        if let Some(buffer) = pool.pop() {
            buffer
        } else {
            BytesMut::with_capacity(4096)
        }
    }
    
    async fn release(&self, mut buffer: BytesMut) {
        buffer.clear();
        let mut pool = self.buffers.lock().await;
        if pool.len() < 100 {
            pool.push(buffer);
        }
    }
}
```