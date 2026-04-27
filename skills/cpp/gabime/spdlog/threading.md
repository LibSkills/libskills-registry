# spdlog — Threading

## Thread Safety by Sink Type

| Sink | Thread-Safe? | Notes |
|------|-------------|-------|
| `stdout_sink` | No | Single-threaded only |
| `stdout_sink_mt` | Yes | Mutex-protected writes |
| `basic_file_sink` | No | Single-threaded only |
| `basic_file_sink_mt` | Yes | Mutex-protected writes |
| `rotating_file_sink` | No | Single-threaded only |
| `rotating_file_sink_mt` | Yes | Mutex-protected writes |
| `daily_file_sink` | No | Single-threaded only |
| `daily_file_sink_mt` | Yes | Mutex-protected writes |

**Rule**: Always use `_mt` variants in multi-threaded applications. Non-`_mt` sinks provide no internal synchronization.

## Async Logger Threading

```cpp
spdlog::init_thread_pool(8192, 1);       // queue_size=8192, threads=1
auto logger = spdlog::create_async<spdlog::sinks::basic_file_sink_mt>("async", "logs/app.log");
```

- Async loggers use a background thread pool to write
- The calling thread pushes log messages onto a lock-free SPSC queue
- Queue overflow policy (set via template parameter): `block` (default), `overrun_oldest`, `discard_new`
- One thread is sufficient for most workloads; more threads increase contention

## Async Overflow Policy

| Policy | Behavior when queue is full |
|--------|---------------------------|
| `block` | Blocks the calling thread until space is available (default) |
| `overrun_oldest` | Drops the oldest message, inserts the new one |
| `discard_new` | Drops the new message, keeps the oldest |

## Thread-Local Registry

spdlog's logger registry is thread-safe. Registering loggers, setting the default logger, and retrieving loggers by name are all protected by an internal mutex.
