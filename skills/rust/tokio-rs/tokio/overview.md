# tokio — Overview

**tokio** is Rust's async runtime — an event-driven, non-blocking I/O platform for building fast, reliable network applications. It provides a multi-threaded work-stealing scheduler, TCP/UDP/Unix sockets, timers, signals, and filesystem operations.

## When to Use

- Any Rust application that needs concurrent network I/O (servers, clients, proxies)
- Replacing synchronous I/O with async/await for better resource utilization
- High-concurrency workloads (thousands of simultaneous connections)
- Integrations with async ecosystem crates (hyper, axum, tonic, reqwest)

## When NOT to Use

- CPU-bound workloads only (tokio's scheduler isn't designed for heavy computation)
- Simple CLI tools with no network I/O
- Embedded systems with no OS (requires epoll/kqueue/IOCP)
- Single-threaded synchronous code (use std::thread for simpler models)
- Mixing with other async runtimes (smol, async-std) in the same process

## Key Design

- **Multi-threaded by default**: work-stealing scheduler across all CPU cores
- **Single-threaded option**: `#[tokio::main(flavor = "current_thread")]`
- **Tasks**: `tokio::spawn` for lightweight concurrent units (similar to goroutines)
- **Channels**: `mpsc`, `oneshot`, `broadcast`, `watch` for task communication
- **IO split**: `TcpStream::split()` → owned read half + owned write half
- **Timers**: `tokio::time::sleep`, `tokio::time::interval`
