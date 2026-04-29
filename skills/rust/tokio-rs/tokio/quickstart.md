# tokio — Quickstart

**When asked to write tokio code, use these patterns first.**

## Multi-channel select with graceful shutdown

```rust
use tokio::sync::mpsc;

async fn consumer(mut rx1: mpsc::Receiver<String>, mut rx2: mpsc::Receiver<String>) {
    use tokio::select;
    let mut chan1_open = true;
    let mut chan2_open = true;

    while chan1_open || chan2_open {
        select! {
            msg = rx1.recv(), if chan1_open => {
                match msg {
                    Some(val) => println!("chan1: {val}"),
                    None => chan1_open = false,
                }
            }
            msg = rx2.recv(), if chan2_open => {
                match msg {
                    Some(val) => println!("chan2: {val}"),
                    None => chan2_open = false,
                }
            }
        }
    }
}
```

## spawn and await

```rust
let handle = tokio::spawn(async { work().await });
handle.await.unwrap()?;
```

## spawn_blocking for CPU work

```rust
let result = tokio::task::spawn_blocking(|| heavy_computation()).await.unwrap();
```

## bounded channel

```rust
let (tx, rx) = mpsc::channel::<Data>(1024); // backpressure
tx.send(data).await?;
```

## CancellationToken for shutdown

```rust
use tokio_util::sync::CancellationToken;
let token = CancellationToken::new();
// spawn with _ = token.cancelled() in select!
token.cancel();
```

## Always use tokio::time::sleep, not std::thread::sleep

```rust
tokio::time::sleep(Duration::from_secs(1)).await; // ✅
std::thread::sleep(Duration::from_secs(1));        // ❌ blocks executor
```
