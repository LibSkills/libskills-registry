# spdlog — Pitfalls (Compact)

**Critical mistakes to avoid. Read this before generating spdlog code.**

## 1. Thread Safety: Use `_mt` suffix ❌→✅

```cpp
// BAD: NOT thread-safe
auto sink = std::make_shared<spdlog::sinks::basic_file_sink>("log.txt");

// GOOD: thread-safe
auto sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>("log.txt");
```

## 2. Resource Cleanup: Call `shutdown()` ❌→✅

```cpp
// BAD: resource leak
int main() { /* ... */ }

// GOOD: clean shutdown
int main() {
    // ... your code ...
    spdlog::shutdown();
    return 0;
}
```

## 3. Static Destructors: Don't log there ❌→✅

```cpp
// BAD: undefined behavior
static MyThing global_thing;  // destructor logs → crash

// GOOD: use atexit or main()
int main() {
    spdlog::shutdown();
    return 0;
}
```

## 4. Format Strings: Use `{}` not `+` ❌→✅

```cpp
// BAD: memory allocation + flush
logger->info("Value: " + std::to_string(x) + "\n");

// GOOD: spdlog handles formatting
logger->info("Value: {}", x);
```

## 5. Async Queue: Size appropriately ❌→✅

```cpp
// BAD: may drop messages
spdlog::init_thread_pool(256, 1);

// GOOD: size for expected load
spdlog::init_thread_pool(8192, 1);
```

## 6. fork(): Recreate loggers ❌→✅

```cpp
// BAD: inconsistent state
if (fork() == 0) { logger->info("child"); }

// GOOD: recreate
if (fork() == 0) {
    auto child_logger = spdlog::rotating_logger_mt("child", "child.log", 1048576, 3);
}
```

## 7. Don't use `std::endl` ❌→✅

```cpp
// BAD: flushes every write
logger->info("Value: {}\n", x);

// GOOD: let spdlog handle buffering
logger->info("Value: {}", x);
```

**Summary**: Always use `_mt`, call `shutdown()`, avoid static destructors, use `{}` format.