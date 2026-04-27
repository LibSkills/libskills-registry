# tokio — Safety

Red lines — conditions that must NEVER occur.

## NEVER call blocking I/O (std::net, std::fs) inside an async task

Blocking I/O on the executor thread stalls ALL tasks on that worker. This is the #1 cause of mysterious tokio performance regressions.

```rust
// NEVER: freezes the executor thread
async fn bad() {
    let data = std::fs::read_to_string("file.txt")?; // blocks ALL tasks
}

// ALWAYS: spawn_blocking for synchronous work
async fn good() {
    let data = tokio::task::spawn_blocking(|| std::fs::read_to_string("file.txt"))
        .await??;
}
```

## NEVER hold a std::sync::Mutex across .await

This compiles only if you carefully scope the lock guard. If you accidentally hold the guard across `.await`, the compiler error is the safety check. Don't suppress it with unsafe or `block_in_place`.

```rust
// NEVER: deadlock or compile error
let guard = std_mutex.lock().unwrap();
some_async_fn().await; // guard held across .await
```

## NEVER spawn_blocking inside a current_thread runtime without care

`spawn_blocking` creates OS threads. On a `current_thread` runtime, the main thread is the only worker — blocking it means no progress until the blocking task completes.

## NEVER create multiple runtimes in the same process

Multiple `tokio::runtime::Runtime` instances in the same process cause thread pool over-subscription, confusing task scheduling, and undebuggable deadlocks. Use one runtime.

```rust
// NEVER: two runtimes
#[tokio::main]
async fn main() {
    let rt2 = tokio::runtime::Runtime::new().unwrap(); // BAD
}
```

## NEVER send secrets or unbounded data through channels without backpressure

`tokio::sync::mpsc::unbounded_channel()` has no backpressure. An unbounded producer can exhaust memory. Always prefer bounded channels for production.

```rust
// GOOD: bounded channel with backpressure
let (tx, rx) = tokio::sync::mpsc::channel::<Data>(1024);
```

## NEVER abort a task that holds resources without cleanup

`JoinHandle::abort()` cancels the task at the next `.await`. If the task holds resources (file handles, locks, DB connections), they leak. Always use RAII or explicit cleanup before aborting.
