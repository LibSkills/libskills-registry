# Gin — Overview

**Gin** is a high-performance HTTP web framework for Go. It provides a martini-like API with significantly better performance — up to 40x faster thanks to its custom `httprouter` (a radix-tree-based router).

## When to Use

- Building RESTful APIs and microservices in Go
- Need fast routing with path parameters (`/users/:id`) and query string parsing
- Want built-in middleware chaining, request binding/validation, and graceful shutdown
- Building JSON-based HTTP services with minimal boilerplate

## When NOT to Use

- Full-stack web apps requiring server-side templating (consider Echo or Fiber for similar performance with more features)
- WebSocket-heavy applications (Gin supports it but is not optimized for it)
- Applications that need gRPC-native transport (use `grpc-go` directly)
- Ultra-low-latency high-frequency trading or similar (Go's GC and runtime still apply)

## Key Design

- **Router tree**: Uses a compressed radix tree for path matching — no reflection, no iteration over routes
- **Middleware chain**: `gin.HandlerFunc` functions in a chain; `c.Next()` passes control to the next handler
- **Context**: `*gin.Context` is the central object — carries request, response, params, and custom key-value store
- **Binding + validation**: Automatic request body binding to structs with struct tags; uses `go-playground/validator` under the hood
- **Error management**: `c.Error()` / `c.Errors()` collects errors without aborting the request
