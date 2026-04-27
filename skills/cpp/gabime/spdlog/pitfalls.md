# spdlog — Pitfalls

Common mistakes that cause crashes, data loss, or silent misbehavior.

## Do NOT use the default logger in static destructors

The default logger may already be destroyed by the time a static destructor runs. Logging in a static destructor can crash or produce no output.

```cpp
// BAD: undefined behavior
static MyThing global_thing;
// MyThing::~MyThing() uses spdlog::info() — logger may be gone

// GOOD: use atexit or explicit shutdown ordering
```

## Do NOT use std::endl

`std::endl` flushes on every write. spdlog is binary-safe and handles buffering internally. Use `\n` in format strings.

```cpp
// BAD
logger->info("Value: {}" + std::to_string(x) + "\n"); // memory allocation + flush

// GOOD
logger->info("Value: {}", x);
```

## Do NOT pass temporary strings for format arguments

spdlog format arguments are stored by reference (fmt underneath). A temporary string's lifetime expires before the format call completes.

```cpp
// BAD
logger->info("Value: {}", std::to_string(x)); // temporary destroyed, dangling ref

// GOOD
logger->info("Value: {}", x); // spdlog handles format conversion
```

## Do NOT call shutdown() in a static destructor

`spdlog::shutdown()` drops all loggers. Calling it in a static destructor races with other static destructors that may also drop loggers. Use `atexit()` or call `shutdown()` explicitly in `main()`.

```cpp
// BAD
struct Cleaner { ~Cleaner() { spdlog::shutdown(); } };
static Cleaner cleaner; // may double-drop

// GOOD
int main() { spdlog::shutdown(); return 0; }
```

## Do NOT share non-mt sinks across threads

Sinks without `_mt` suffix are NOT thread-safe. Use `_mt` variants for multi-threaded logging.

```cpp
// BAD: crash or corrupted output
auto sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>("log.txt");
std::thread t1([&]{ logger->info("thread 1"); });
std::thread t2([&]{ logger->info("thread 2"); });

// GOOD: _mt suffix
auto sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>("log.txt");
```

## Do NOT use spdlog after fork() without recreating

After `fork()`, child process inherits loggers but underlying file descriptors may be in an inconsistent state. Always recreate loggers in the child.

```cpp
// BAD
if (fork() == 0) {
    logger->info("child"); // undefined behavior
}

// GOOD
if (fork() == 0) {
    auto child_logger = spdlog::rotating_logger_mt("child", "child.log", 1048576, 3);
}
```

## Do NOT set an async queue too small

Async logger drops messages silently when the queue is full (default overflow policy: `block`). Choose `queue_size` based on peak throughput.

```cpp
// BAD: may drop messages under load
spdlog::init_thread_pool(256, 1);

// GOOD: size for expected load
spdlog::init_thread_pool(8192, 1);
```
