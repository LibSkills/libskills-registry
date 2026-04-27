# spdlog — Performance

## Throughput (approximate, modern x86_64)

| Mode | Logs/sec | Latency (p50) | Notes |
|------|----------|---------------|-------|
| Sync, single thread | ~500K/s | ~2µs | Blocking per write |
| Async, 1 thread pool | ~2M/s | ~0.5µs | Non-blocking from caller |
| Async, 4 thread pool | ~3-5M/s | ~0.3µs | Diminishing returns |
| Sync with flush on every log | ~10K/s | ~100µs | Disk-bound |

## Performance Rules

- **Async >> sync** for throughput-sensitive code. The caller doesn't wait for I/O.
- **Batch formatting**: spdlog formats the entire message once, not per-sink.
- **Compile-time level filtering**: `SPDLOG_ACTIVE_LEVEL` set to `SPDLOG_LEVEL_INFO` makes trace/debug calls compile to no-ops.
- **Avoid flush-on-every-log**: `logger->flush_on(spdlog::level::info)` forces a disk flush per log. Only use for critical errors.
- **Queue size**: 8192 is a good default. Too small = blocking under load. Too large = memory waste.

## Sink Performance

| Sink | Note |
|------|------|
| `stdout_sink_mt` | Fast (memory-mapped I/O on Linux) |
| `rotating_file_sink_mt` | Moderate overhead (check rotation on every write) |
| `daily_file_sink_mt` | Moderate overhead (date calculation per write) |
| `syslog_sink` | Slowest (syscall per message) |

## Benchmark Code

```cpp
#include <spdlog/spdlog.h>
#include <spdlog/async.h>
#include <chrono>

void benchmark() {
    spdlog::init_thread_pool(8192, 1);
    auto logger = spdlog::create_async<spdlog::sinks::basic_file_sink_mt>(
        "bench", "/dev/null");
    
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < 1'000'000; i++) {
        logger->info("benchmark message {}", i);
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    spdlog::info("1M logs in {}ms = {} logs/sec", ms, 1'000'000 * 1000 / ms);
}
```
