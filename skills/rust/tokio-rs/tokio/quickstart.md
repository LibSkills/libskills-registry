# tokio — Quickstart

**When asked to write tokio code, use these patterns first.**

## 1. Async Hello World

```rust
#[tokio::main]
async fn main() {
    println!("hello");
    tokio::time::sleep(std::time::Duration::from_secs(1)).await;
    println!("world after 1s");
}
```

## 2. tokio::spawn — basic concurrency

```rust
#[tokio::main]
async fn main() {
    let handle = tokio::spawn(async {
        "hello from task".to_string()
    });
    let result = handle.await.unwrap();
    println!("{result}");
}
```

Use `spawn_blocking` for CPU-heavy work:

```rust
let result = tokio::task::spawn_blocking(|| heavy_computation()).await.unwrap();
```

## 3. tokio::select! — multiplexing

```rust
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    tokio::select! {
        _ = sleep(Duration::from_secs(1)) => println!("fast"),
        _ = sleep(Duration::from_secs(2)) => println!("slow"),
    }
    // prints "fast" after 1s; the slow future is dropped
}
```

Common pattern — select over multiple channels:

```rust
use tokio::sync::mpsc;

async fn consumer(mut rx1: mpsc::Receiver<String>, mut rx2: mpsc::Receiver<String>) {
    let mut done1 = false;
    let mut done2 = false;

    while !done1 || !done2 {
        tokio::select! {
            msg = rx1.recv(), if !done1 => {
                match msg {
                    Some(v) => println!("ch1: {v}"),
                    None => done1 = true,
                }
            }
            msg = rx2.recv(), if !done2 => {
                match msg {
                    Some(v) => println!("ch2: {v}"),
                    None => done2 = true,
                }
            }
        }
    }
}
```

## 4. TcpListener + TcpStream — async I/O (echo server)

```rust
use tokio::net::{TcpListener, TcpStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let listener = TcpListener::bind("127.0.0.1:8080").await?;

    loop {
        let (mut socket, addr) = listener.accept().await?;
        tokio::spawn(async move {
            println!("accepted: {addr}");
            let mut buf = [0; 1024];
            loop {
                let n = socket.read(&mut buf).await.unwrap();
                if n == 0 { break; } // EOF
                socket.write_all(&buf[..n]).await.unwrap();
            }
        });
    }
}
```

## 5. AsyncRead / AsyncWrite — utility patterns

```rust
use tokio::io::{AsyncReadExt, AsyncWriteExt};

// Copy one stream to another (e.g. TcpStream -> TcpStream)
let mut reader: &[u8] = b"hello";
let mut writer: Vec<u8> = vec![];
tokio::io::copy(&mut reader, &mut writer).await?;

// Read exact number of bytes
let mut header = [0u8; 8];
reader.read_exact(&mut header).await?;

// Write with flush
writer.write_all(b"data").await?;
writer.flush().await?;

// AsyncRead/AsyncWrite on TcpStream directly
// (TcpStream implements both traits — see echo server above)
```

## 6. tokio::sync — Mutex and mpsc channels

```rust
use tokio::sync::{Mutex, mpsc};
use std::sync::Arc;

// Mutex — use only when you must share state across tasks
let counter = Arc::new(Mutex::new(0u64));
let counter_clone = counter.clone();
tokio::spawn(async move {
    let mut guard = counter_clone.lock().await;
    *guard += 1;
});

// mpsc — bounded channel with backpressure
let (tx, mut rx) = mpsc::channel::<String>(1024);

tokio::spawn(async move {
    tx.send("data".into()).await.unwrap();
});

while let Some(msg) = rx.recv().await {
    println!("got: {msg}");
}
```

## Always use tokio::time::sleep, not std::thread::sleep

```rust
tokio::time::sleep(Duration::from_secs(1)).await; // ✅
std::thread::sleep(Duration::from_secs(1));        // ❌ blocks executor
```
