# Overview

smol is a lightweight, single-threaded async runtime for C++ that provides an efficient executor for coroutines and async I/O operations. It's designed for applications that don't need the complexity of multi-threaded runtimes like asio or libuv.

**When to use smol:**
- Building simple async network services (TCP/UDP servers/clients)
- Creating command-line tools with async I/O
- Prototyping async applications quickly
- Embedded or resource-constrained environments
- Single-threaded event-driven applications

**When NOT to use smol:**
- CPU-bound parallel workloads (use std::thread or TBB instead)
- Applications requiring multi-threaded executors
- Real-time systems with strict latency requirements
- Large-scale distributed systems needing complex scheduling

**Key design principles:**
- Single-threaded execution model (no thread pool)
- Work-stealing from async tasks
- Cooperative multitasking via coroutines
- Minimal overhead compared to full-featured runtimes
- Built on top of epoll/kqueue/IOCP for I/O