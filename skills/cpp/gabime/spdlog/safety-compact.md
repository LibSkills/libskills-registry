# spdlog — Safety Rules (Compact)

**NEVER do these things. They will crash your application.**

## 🔴 RED LINES — Absolutely Forbidden

### 1. Never log in static destructors
```cpp
// ❌ CRASH: logger may be destroyed
static MyThing global_thing;
// MyThing::~MyThing() uses spdlog::info()

// ✅ SAFE: use main() or atexit
int main() {
    // ... your code ...
    spdlog::shutdown();
}
```

### 2. Never use `_st` (single-threaded) sinks in multi-threaded code
```cpp
// ❌ CRASH: race condition
auto sink = std::make_shared<spdlog::sinks::basic_file_sink>("log.txt");
std::thread t1([&]{ logger->info("thread 1"); });
std::thread t2([&]{ logger->info("thread 2"); });

// ✅ SAFE: use `_mt` suffix
auto sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>("log.txt");
```

### 3. Never forget to call `shutdown()`
```cpp
// ❌ RESOURCE LEAK: loggers not cleaned up
int main() {
    auto logger = spdlog::rotating_logger_mt("app", "app.log", 1048576, 3);
    logger->info("started");
    // ... your code ...
    return 0;
}

// ✅ SAFE: always shutdown
int main() {
    auto logger = spdlog::rotating_logger_mt("app", "app.log", 1048576, 3);
    logger->info("started");
    // ... your code ...
    spdlog::shutdown();
    return 0;
}
```

### 4. Never pass temporary strings to format
```cpp
// ❌ UNDEFINED BEHAVIOR: dangling reference
logger->info("Value: {}", std::to_string(x));

// ✅ SAFE: let spdlog handle conversion
logger->info("Value: {}", x);
```

### 5. Never use spdlog after `fork()` without recreating
```cpp
// ❌ UNDEFINED BEHAVIOR: inconsistent file descriptors
if (fork() == 0) {
    logger->info("child process");
}

// ✅ SAFE: recreate logger in child
if (fork() == 0) {
    auto child_logger = spdlog::rotating_logger_mt("child", "child.log", 1048576, 3);
    child_logger->info("child process");
}
```

## ⚠️ Critical Checks

Before compiling, verify:
- [ ] All sinks use `_mt` suffix
- [ ] `spdlog::shutdown()` called in main()
- [ ] No logging in static destructors
- [ ] No `std::to_string()` in format args
- [ ] Async queue size ≥ 1024

**Remember**: When in doubt, use `_mt` and call `shutdown()`.