# net/http — Overview

**net/http** is Go's standard library package for building HTTP servers and clients. It provides a complete HTTP/1.1 implementation with HTTP/2 support (via HTTP/2 "h2" and "h2c"), and requires no third-party dependencies.

## When to Use

- Building REST APIs, microservices, or web applications in Go
- Making outgoing HTTP requests to external services
- Serving static files or implementing reverse proxies
- Any Go HTTP work where you want zero external dependencies

## When NOT to Use

- Complex routing with path parameters and middleware chaining (Go 1.22+ improves this significantly, but frameworks like Gin, Echo, or Chi provide richer routing DSLs)
- Applications requiring WebSocket or SSE out of the box (net/http supports hijacking connections but you need a library like `gorilla/websocket` on top)
- High-throughput services needing custom connection management (the default transport is well-tuned but advanced use cases may need `fasthttp` or a tuned `http.Transport`)

## Key Design

- **`http.Handler` interface**: The core abstraction — any type implementing `ServeHTTP(ResponseWriter, *Request)` is a handler
- **`http.HandlerFunc`**: Adapter type that turns a plain function into a `Handler` — enables middleware patterns
- **`ServeMux`**: Request router (Go 1.22+ supports method-based routing and path parameters)
- **`http.Client`**: HTTP client with configurable `Transport`, timeouts, and redirect policy
- **`http.Transport`**: Connection pool for client — controls keep-alive, connection limits, TLS config
- **`ResponseWriter`**: Interface for writing response headers and body; also implements `http.Hijacker` and `http.Flusher`
- **`http.Request`**: Represents an incoming HTTP request — body, headers, URL, context

## Versions

- **Go 1.22+**: `ServeMux` now supports `GET /path/{param}` and `POST /path/{param}` style routing with method matching
- **Go 1.20+**: `ResponseController` allows per-handler access to Flusher, Hijacker, and Pusher without type assertions
- **Go 1.7+**: Request context via `context.Context` built into `*http.Request`
