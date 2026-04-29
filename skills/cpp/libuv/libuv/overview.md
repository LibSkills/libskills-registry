# Overview

libuv is a cross-platform asynchronous I/O library originally developed for Node.js. It provides an event-driven, non-blocking I/O model that handles network sockets, file system operations, DNS resolution, timers, signals, and child processes through a single event loop.

**When to use libuv:**
- Building high-performance network servers or clients
- Implementing event-driven architectures
- Cross-platform applications requiring async I/O
- Embedding a JavaScript runtime (Node.js uses it internally)
- Applications needing fine-grained control over the event loop

**When NOT to use libuv:**
- Simple synchronous I/O tasks (use standard C++ I/O instead)
- When you need HTTP protocol handling (use a dedicated HTTP library)
- GUI applications (use platform-specific event loops)
- CPU-bound workloads (libuv excels at I/O, not computation)

**Key Design Principles:**
- Single-threaded event loop with thread pool for blocking operations
- Handle-based API (uv_tcp_t, uv_timer_t, etc.) with request objects for operations
- Non-blocking I/O with callback-based completion notifications
- Cross-platform abstraction over epoll (Linux), kqueue (macOS), IOCP (Windows), and event ports (Solaris)