# spdlog — Lifecycle

## Initialization

```cpp
#include <spdlog/spdlog.h>

// Option 1: Use the default logger (auto-created)
spdlog::info("Hello");  // writes to stdout by default

// Option 2: Create a custom logger
auto logger = spdlog::stdout_color_mt("my_logger");
spdlog::set_default_logger(logger);

// Option 3: Async logger
spdlog::init_thread_pool(8192, 1);
auto async_logger = spdlog::create_async<spdlog::sinks::rotating_file_sink_mt>(
    "async", "logs/app.log", 1048576 * 5, 3);
spdlog::set_default_logger(async_logger);
```

## Registration Order

- Call `spdlog::set_default_logger()` before any code (including static initializers) logs
- If a static initializer calls `spdlog::info()`, it will use the default stdout logger — make sure your custom logger is registered first
- Use `spdlog::register_logger()` if you need multiple named loggers without changing the default

## Shutdown

```cpp
int main() {
    // ... application code ...

    spdlog::shutdown(); // flushes all loggers, releases resources
    return 0;
}
```

**Rules:**
- Always call `spdlog::shutdown()` before process exit
- NEVER call `shutdown()` inside a static destructor (logger may already be destroyed)
- NEVER call `shutdown()` more than once (idempotent but wasteful)
- DO call `logger->flush()` before destroying a specific logger if you need guarantees

## After fork()

```cpp
pid_t pid = fork();
if (pid == 0) {
    // Child: recreate all loggers
    spdlog::drop_all(); // release inherited loggers
    auto logger = spdlog::rotating_logger_mt("child", "child.log", 1048576, 3);
    spdlog::set_default_logger(logger);
} else {
    // Parent: continue using existing loggers normally
}
```
