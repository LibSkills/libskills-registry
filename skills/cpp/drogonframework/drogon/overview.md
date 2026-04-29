# Overview

Drogon is a high-performance C++17/20 web application framework designed for building HTTP servers, REST APIs, and WebSocket services. It provides an asynchronous, event-driven architecture using a non-blocking I/O model based on epoll (Linux) or kqueue (macOS). The framework includes built-in ORM support, JSON handling, WebSocket management, and a plugin system.

Use Drogon when you need a production-grade C++ web server with low latency and high throughput, especially for microservices, real-time applications, or systems requiring tight resource control. Avoid Drogon for simple prototypes or when you need extensive middleware ecosystems like Express.js or Spring Boot.

Key design principles include:
- Asynchronous by default: All I/O operations are non-blocking
- Event-driven architecture using reactor pattern
- Zero-copy data transfer where possible
- Built-in connection pooling for databases
- Template-based routing with compile-time validation