# tokio — Performance

## Throughput

| Config | TCP echo (req/s) | Notes |
|--------|-----------------|-------|
| Multi-thread, 8 workers | ~500K/s | Good for mixed I/O |
| Current-thread | ~200K/s | CPU-bound by single core |
| spawn_blocking (512 threads) | N/A | Thread creation overhead |

## Key Performance Rules

- **spawn_blocking is expensive**: each call dispatches to OS thread pool (~10µs overhead)
- **Bounded channels are faster**: lock-free SPSC queues outperform unbounded (alloc-heavy) channels
- **worker_threads = num_cpus**: oversubscribing hurts cache locality, undersubscribing starves I/O
- **tokio::sync::Mutex is slower than std::sync::Mutex** for non-async contention: use std mutex when not held across .await

## I/O Performance

- `tokio::net::TcpStream` is equivalent to epoll-based async I/O — zero overhead vs raw epoll
- `tokio::fs` operations spawn blocking threads internally (same as `spawn_blocking`)
- For high-throughput file I/O, use `tokio::fs::File` for async but prefer `spawn_blocking` with `std::fs` for large sequential reads

## Memory

- Each spawned task: ~3KB stack + future state (depends on `.await` points)
- Work-stealing queues: 256 slots per worker by default
- `tokio::sync::mpsc::channel(1024)`: ~16KB for the channel buffer

## Benchmarking

```rust
use std::time::Instant;
use tokio::net::TcpListener;

#[tokio::main]
async fn main() {
    let listener = TcpListener::bind("0.0.0.0:8080").await.unwrap();
    let start = Instant::now();
    let mut count = 0u64;

    loop {
        let (mut sock, _) = listener.accept().await.unwrap();
        tokio::spawn(async move {
            let mut buf = [0u8; 1024];
            let n = sock.read(&mut buf).await.unwrap();
            sock.write_all(&buf[..n]).await.unwrap();
        });
        count += 1;
        if start.elapsed().as_secs() >= 1 {
            println!("{} req/s", count);
            count = 0;
        }
    }
}
```
