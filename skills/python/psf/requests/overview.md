# requests — Overview

**requests** is the de-facto standard HTTP client library for Python. It provides a clean, idiomatic API for making HTTP requests with automatic connection pooling, SSL/TLS verification, cookie persistence, redirect following, and multipart file uploads.

## When to Use

- Any Python application that makes HTTP requests (REST APIs, web scraping, file downloads)
- Scripts and CLI tools that interact with web services
- Prototyping HTTP interactions
- Testing HTTP endpoints

## When NOT to Use

- High-concurrency applications (requests is synchronous/blocking — use `httpx` with async or `aiohttp`)
- Streaming large numbers of concurrent connections (use an async HTTP client)
- Server-side request handling (requests is a client library)
- WebSocket connections (use `websockets` or `websocket-client`)

## Key Design

- **Synchronous**: every call blocks the calling thread until the response arrives
- **Session**: `requests.Session()` for connection reuse, cookie persistence, default headers
- **Automatic features**: redirect following, gzip/deflate decompression, content decoding
- **SSL**: verification enabled by default (`verify=True`); uses `certifi` CA bundle
- **Timeout**: `timeout` parameter controls connect and read timeouts — NOT set by default
