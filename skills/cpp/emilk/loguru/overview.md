# Overview

Loguru is a lightweight, single-header C++ logging library designed for simplicity and performance. It provides printf-style and stream-style logging with verbosity levels, assertions, stack traces, and scope-based indentation.

**When to use:**
- You need a minimal logging library with no dependencies
- You want fast compile times (header has no #includes)
- You need thread-safe logging with file output support
- You want grep-able log output for production debugging
- You need stack traces on crashes and assertions

**When NOT to use:**
- You need a full-featured logging framework with syslog integration
- You require structured JSON logging out of the box
- You need runtime-configurable logging without recompilation
- You're targeting platforms without C++11 support

**Key design:**
- Two-file library: `loguru.hpp` and `loguru.cpp`
- No header includes for minimal compilation overhead
- Verbosity levels 0-9 (0=FATAL, 1=ERROR, 2=WARNING, 3=INFO, 4-9=DEBUG)
- Scope-based indentation for hierarchical logging
- Error context capture for crash debugging
- Background thread flushing for performance