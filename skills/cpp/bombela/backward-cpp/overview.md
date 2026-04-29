# Overview


Backward-cpp is a header-only C++ library that provides beautiful, detailed stack trace printing for debugging and error reporting. It automatically captures and formats stack traces when fatal signals occur (segfault, abort, etc.) or on demand, showing source file names, line numbers, function names, and even code snippets when debug symbols are available.

**When to use:**
- Debugging crashes in production or development
- Adding detailed error reporting to logging systems
- Understanding complex call stacks in multithreaded applications
- Replacing basic `backtrace_symbols()` output with readable traces

**When NOT to use:**
- In performance-critical code paths (stack trace capture is expensive)
- When binary size must be minimized (debug symbols add size)
- On embedded systems with limited resources
- When you need cross-platform support beyond Linux, macOS, and Windows

**Key design principles:**
- Header-only core (`backward.hpp`) with optional implementation file (`backward.cpp`) for signal handling
- Supports multiple backends: libbfd, libdw, libdwarf, and basic `backtrace_symbols`
- Configurable output with source snippets, colors, and address display
- Signal handlers are registered globally and are NOT thread-safe by default