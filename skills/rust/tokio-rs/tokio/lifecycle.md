# tokio — Lifecycle

## Runtime Creation

```rust
#[tokio::main]
async fn main() {
    // Multi-threaded (default): work-stealing across all cores
    // ...
}

// Or manually:
fn main() {
    let rt = tokio::runtime::Runtime::new().unwrap();
    rt.block_on(async {
        // ...
    });
}
```

## Shutdown

- `rt.shutdown_background()` — signals shutdown, waits for spawned tasks to complete
- `rt.shutdown_timeout(Duration)` — waits up to timeout, then aborts remaining tasks
- Tasks detect shutdown via `CancellationToken` or checking channel closure

```rust
let rt = tokio::runtime::Runtime::new().unwrap();
rt.spawn(async {
    tokio::time::sleep(Duration::from_secs(10)).await;
});
rt.shutdown_timeout(Duration::from_secs(5)); // waits 5s, then aborts
```

## Current-Thread Runtime

```rust
#[tokio::main(flavor = "current_thread")]
async fn main() {
    // Single thread — no work-stealing
    // Use for IO-bound tasks, NOT mixed CPU+IO
}
```

## Task Lifecycle

- `tokio::spawn()` — fire and return JoinHandle
- `JoinHandle::await` — wait for task result
- `JoinHandle::abort()` — cancel task at next .await
- `AbortHandle` — cancel without owning the JoinHandle

```rust
let (abort_handle, abort_registration) = AbortHandle::new_pair();
let handle = tokio::spawn(async {
    abort_registration.await; // cooperatively check cancellation
    Ok::<_, ()>(())
});
abort_handle.abort();
```

## Graceful Shutdown

```rust
use tokio_util::sync::CancellationToken;
let token = CancellationToken::new();

// Spawn workers
for i in 0..4 {
    let token = token.clone();
    tokio::spawn(async move {
        tokio::select! {
            _ = token.cancelled() => {},
            _ = do_work() => {},
        }
    });
}

// Signal shutdown after Ctrl+C
tokio::signal::ctrl_c().await.unwrap();
token.cancel();
```
