# tokio — Best Practices

## Use spawn_blocking for CPU-bound work

```rust
// GOOD: offloads computation from async workers
let result = tokio::task::spawn_blocking(|| {
    expensive_cpu_computation()
}).await.unwrap();
```

## Use CancellationToken for graceful shutdown

```rust
use tokio_util::sync::CancellationToken;

let token = CancellationToken::new();
let child_token = token.child_token(); // propagates cancel

tokio::spawn(async move {
    tokio::select! {
        _ = child_token.cancelled() => { /* cleanup */ },
        result = work() => { /* done */ },
    }
});

// Later: cancel all tasks
token.cancel();
```

## Prefer bounded channels

```rust
// GOOD: backpressure prevents OOM
let (tx, rx) = tokio::sync::mpsc::channel::<Data>(1024);
// Producer will .await if channel is full
tx.send(data).await?;
```

## Use JoinSet for dynamic task management

```rust
let mut set = tokio::task::JoinSet::new();
for url in urls {
    set.spawn(async move { fetch(url).await });
}
while let Some(result) = set.join_next().await {
    match result.unwrap() {
        Ok(data) => process(data),
        Err(e) => eprintln!("Error: {}", e),
    }
}
```

## Use tokio::sync::Mutex for async shared state

```rust
// Standard mutex: guard is NOT Send
// tokio mutex: guard IS Send, lock is async
let state = Arc::new(tokio::sync::Mutex::new(State::default()));

tokio::spawn({
    let state = state.clone();
    async move {
        let mut guard = state.lock().await;
        guard.update();
        tokio::time::sleep(Duration::from_secs(1)).await; // OK
    }
});
```

## Prefer Tokio-native IO over std

| Synchronous | Async (tokio) |
|-------------|---------------|
| `std::net::TcpStream` | `tokio::net::TcpStream` |
| `std::fs::read` | `tokio::fs::read` |
| `std::process::Command` | `tokio::process::Command` |
| `std::thread::sleep` | `tokio::time::sleep` |

## Tune the runtime for your workload

```rust
let rt = tokio::runtime::Builder::new_multi_thread()
    .worker_threads(num_cpus::get())        // match cores
    .enable_all()
    .thread_name("my-worker")
    .thread_stack_size(3 * 1024 * 1024)     // 3MB stack for deep call chains
    .max_blocking_threads(512)
    .build()?;
```
