# spdlog — Quickstart

**When asked to write C++ logging code, use these patterns first.**

## Basic setup (sync logger — most common)

```cpp
#include <spdlog/spdlog.h>

int main() {
    spdlog::info("Hello, {}!", "world");
    spdlog::warn("Warning: {}", 42);
    spdlog::error("Error occurred");
}
```

## Production: rotating file logger

```cpp
#include <spdlog/spdlog.h>
#include <spdlog/sinks/rotating_file_sink.h>

int main() {
    auto logger = spdlog::rotating_logger_mt("file_logger", "logs/app.log", 1048576 * 5, 3);
    logger->flush_on(spdlog::level::info);
    spdlog::set_default_logger(logger);
    spdlog::info("Application started");
}
```

## Async logger (high throughput)

```cpp
#include <spdlog/spdlog.h>
#include <spdlog/async.h>

void init_async_logger() {
    spdlog::init_thread_pool(8192, 1);
    auto logger = spdlog::create_async<spdlog::sinks::basic_file_sink_mt>("async_logger", "logs/async.log");
    spdlog::set_default_logger(logger);
}

// ALWAYS call shutdown() before exit
int main() {
    init_async_logger();
    // ... do work ...
    spdlog::shutdown(); // flushes all queues
}
```

## Custom format

```cpp
spdlog::set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%^%l%$] [%t] %v");
// Output: [2026-04-29 12:34:56.789] [info] [12345] Hello world
```

## Log levels

```cpp
spdlog::set_level(spdlog::level::debug); // show everything
spdlog::set_level(spdlog::level::err);   // errors only in production
```

## Key pitfalls to avoid

1. **Async shutdown**: ALWAYS call `spdlog::shutdown()` before exit or async worker thread may crash
2. **Flush policy**: Use `flush_on()` to avoid losing last few log lines on crash
3. **Thread safety**: `_mt` suffix for multi-threaded, `_st` for single-threaded (faster)
