# tokio — Threading

## Multi-Thread Runtime (Default)

- Spawns `num_cpus` worker threads
- Work-stealing scheduler: idle workers steal tasks from busy workers
- Each worker has its own task queue
- Tasks are `Send + 'static` (can move between threads)

```rust
#[tokio::main]
async fn main() {
    // Spawns N tasks that may run on any worker thread
    for i in 0..100 {
        tokio::spawn(async move {
            // This block may execute on any worker thread
        });
    }
}
```

## Current-Thread Runtime

- Single worker thread only
- Tasks do NOT need to be `Send`
- Useful for !Send types (Rc, RefCell, raw pointers)

```rust
#[tokio::main(flavor = "current_thread")]
async fn main() {
    let rc = Rc::new(42); // OK: single thread
}
```

## spawn_blocking

- Runs blocking code on a dedicated thread pool (not tokio workers)
- Max threads: 512 by default (`max_blocking_threads`)

```rust
let result = tokio::task::spawn_blocking(|| {
    std::thread::sleep(Duration::from_secs(5));
    42
}).await.unwrap();
```

## block_in_place

- Moves the current worker thread temporarily to a blocking pool
- Other tasks on this worker are stolen by other workers
- Use sparingly — disrupts scheduling

## Thread Safety for Shared State

| Type | Async-Safe | Notes |
|------|-----------|-------|
| `tokio::sync::Mutex` | Yes | Designed for .await across lock |
| `std::sync::Mutex` | No | Guard not Send across .await |
| `tokio::sync::RwLock` | Yes | Async read/write lock |
| `std::sync::RwLock` | No | Blocks worker thread |
| `Atomic*` | Yes | Lock-free, no blocking |

## Worker Threads Tuning

```rust
let rt = tokio::runtime::Builder::new_multi_thread()
    .worker_threads(4) // match available cores
    .max_blocking_threads(256)
    .build()?;
```
