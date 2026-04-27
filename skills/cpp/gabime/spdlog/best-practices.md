# spdlog — Best Practices

## Recommended Production Setup

```cpp
// Async logger + rotating file (production)
spdlog::init_thread_pool(8192, 1);

auto sink = std::make_shared<spdlog::sinks::rotating_file_sink_mt>(
    "logs/app.log", 1048576 * 5, 3);  // 5MB per file, 3 rotated files
auto logger = std::make_shared<spdlog::async_logger>(
    "app", sink, spdlog::thread_pool(),
    spdlog::async_overflow_policy::block);

logger->set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%^%l%$] [%t] %v");
logger->set_level(spdlog::level::info);
spdlog::set_default_logger(logger);
```

## Log Level by Environment

```cpp
// Development: verbose
#ifdef DEBUG
    spdlog::set_level(spdlog::level::debug);
#endif

// Production: info and above
spdlog::set_level(spdlog::level::info);

// Per-logger level
auto db_logger = spdlog::get("database");
db_logger->set_level(spdlog::level::warn);  // only warnings and errors
```

## Pattern Strings

| Flag | Description |
|------|-------------|
| `%Y-%m-%d` | ISO date |
| `%H:%M:%S.%e` | Time with milliseconds |
| `%^%l%$` | Colored log level |
| `%t` | Thread ID |
| `%v` | Log message |
| `%n` | Logger name |
| `%P` | Process ID |

## Async vs Sync Decision

| Scenario | Recommendation | Reason |
|----------|---------------|--------|
| CLI tool / script | Sync | No throughput benefit from async |
| Low-frequency logging (< 1k/s) | Sync | Lower overhead, simpler |
| High-throughput (> 100k/s) | Async | Non-blocking for caller threads |
| Latency-sensitive code path | Async | Avoid I/O blocks in hot loop |
| Single-threaded app | Sync | No concurrent access anyway |
| Multi-threaded server | Async + `_mt` | Both throughput and safety |

## Logging Errors from Exceptions

```cpp
try {
    risky_operation();
} catch (const std::exception& e) {
    spdlog::error("risky_operation failed: {}", e.what());
    // Optionally log with context
    spdlog::error("context: user_id={}, request_id={}", user_id, request_id);
}
```
