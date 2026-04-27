# spdlog — Safety

Red lines — conditions that must NEVER occur.

## NEVER use a logger after fork() without recreating it

After `fork()`, the child process shares the parent's loggers. File descriptors, buffers, and internal state are duplicated but may be in an inconsistent state. Always create fresh loggers in the child process.

## NEVER destroy a logger before flush() completes

Destroying a logger while it still has buffered data may lose log entries. Call `logger->flush()` or `spdlog::shutdown()` before destroying all loggers.

## NEVER share a non-mt sink across threads

Sinks without `_mt` suffix (e.g., `basic_file_sink`, `stdout_sink`) lack internal synchronization. Concurrent writes from multiple threads will corrupt output or crash. Always use `_mt` variants for multi-threaded logging.

## NEVER use `%s` format strings

spdlog uses `{}` fmt-style formatting. `%s` will be treated as a literal string, not a format specifier. The library will compile but produce wrong output.

```cpp
// BAD: prints literals "Hello, %s"
logger->info("Hello, %s", "world");

// GOOD: prints "Hello, world"
logger->info("Hello, {}", "world");
```

## NEVER call spdlog::shutdown() inside a static destructor

`shutdown()` drops all registered loggers. If another static destructor tries to log afterward, it will access freed memory. Call `shutdown()` explicitly in `main()` or use `std::atexit()`.

## NEVER log inside a signal handler

spdlog uses locks and may allocate memory. Signal handlers are restricted to async-signal-safe operations only. Logging in a signal handler is undefined behavior and can deadlock.
