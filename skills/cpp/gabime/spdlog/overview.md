# spdlog — Overview

**spdlog** is a fast, header-only C++ logging library. It supports synchronous and asynchronous logging, multiple sink types (console, rotating file, daily file, syslog), custom formatting via the [fmt](https://github.com/fmtlib/fmt) library, and compile-time log level filtering.

## When to Use

- Any C++ application that needs structured, performant logging
- Replacing raw `std::cout`, `std::cerr`, or `printf` in production code
- Async logging for high-throughput scenarios (>1M logs/sec)
- Multi-threaded applications (with `_mt` sinks)

## When NOT to Use

- Ultra-low-latency real-time systems where blocking I/O is unacceptable (use `async_logger` or a dedicated ring-buffer sink)
- Multi-process applications without careful sink configuration (file sinks don't coordinate across processes)
- Logging inside signal handlers (spdlog uses locks internally; only async-signal-safe operations are permitted)

## Key Design

- **Header-only or compiled**: default is header-only; define `SPDLOG_COMPILED_LIB` for faster builds
- **Format strings**: uses `{}` (fmt syntax), NOT `%s`/`%d` (printf syntax)
- **Sinks + loggers**: sinks handle I/O; loggers combine sinks with formatting and level
- **Levels**: `trace`, `debug`, `info`, `warn`, `error`, `critical`, `off`
- **Thread safety suffix**: `_mt` sinks are thread-safe; `_st` sinks are single-threaded
