# tokio — Pitfalls

## Do NOT block inside async functions

Blocking the executor thread starves other tasks. Never call `std::thread::sleep`, `std::io::Read::read`, `Mutex::lock().unwrap()`, or heavy computation directly in async code.

```rust
// BAD: blocks the entire worker thread
async fn handler() {
    std::thread::sleep(Duration::from_secs(5)); // ALL tasks on this thread are blocked
    heavy_computation(); // CPU starvation
}

// GOOD: use async equivalents
async fn handler() {
    tokio::time::sleep(Duration::from_secs(5)).await;
    tokio::task::spawn_blocking(|| heavy_computation()).await.unwrap();
}
```

## Do NOT use std::sync::Mutex across .await points

`std::sync::Mutex` guard is NOT `Send` across `.await`. The compiler will reject it, but the workaround (explicit drop before .await) is error-prone.

```rust
// BAD: won't compile — MutexGuard is not Send
async fn handler(data: Arc<Mutex<State>>) {
    let mut guard = data.lock().unwrap();
    *guard = compute(*guard);
    tokio::time::sleep(Duration::from_secs(1)).await; // ERROR
}

// GOOD: use tokio::sync::Mutex for async or drop guard before .await
async fn handler(data: Arc<tokio::sync::Mutex<State>>) {
    let mut guard = data.lock().await;
    *guard = compute(*guard);
    tokio::time::sleep(Duration::from_secs(1)).await;
}
```

## Do NOT forget to .await spawned tasks

`tokio::spawn` returns a `JoinHandle`. If you drop the handle without awaiting it, the task continues running but you lose error propagation and cancellation.

```rust
// BAD: fire-and-forget, errors silently lost
tokio::spawn(async { fallible_work().await });

// GOOD: store handle and await (or use JoinSet for many tasks)
let handle = tokio::spawn(async { fallible_work().await });
handle.await.unwrap()?;
```

## Do NOT select! on the same future from multiple branches

`select!` polls branches in random order. If the same future appears in multiple `select!` invocations, one poll may consume the value, causing the other to hang.

```rust
// BAD: data race on future consumption
let fut = async { recv.recv().await };
tokio::select! {
    val = fut => {}, // consumes fut
    val = fut => {}, // fut is already consumed — hangs
}
```

## Do NOT cancel spawned tasks by dropping the JoinHandle

Dropping a `JoinHandle` does NOT cancel the spawned task. It detaches the task. Use `JoinHandle::abort()` or `AbortHandle` for cancellation.

## Do NOT set worker_threads too high

Each worker thread adds scheduling overhead. Match to CPU cores unless you have verified I/O saturation.

```rust
// GOOD: default is num_cpus
let rt = tokio::runtime::Builder::new_multi_thread()
    .worker_threads(num_cpus::get())
    .build()?;
```
