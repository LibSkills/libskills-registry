# Overview

```markdown
# Overview of gorilla/mux

## What It Does
gorilla/mux is a powerful URL router and dispatcher for Go HTTP servers. It extends Go's standard `net/http` package with advanced routing capabilities including path parameters, subrouters, middleware chaining, and regex-based route matching.

## When to Use
- Building RESTful APIs with complex routing requirements
- When you need path parameters (e.g., `/users/{id}`)
- When you need route grouping with shared middleware
- When you need method-based routing (GET, POST, etc.)
- When you need regex constraints on route parameters

## When NOT to Use
- For simple APIs with few routes (standard `net/http` is sufficient)
- When you need high-performance routing (consider `httprouter` or `chi`)
- When you need OpenAPI/Swagger integration (consider `go-chi` with middleware)
- For gRPC-based services

## Key Design Principles
1. **Router as Handler**: `mux.Router` implements `http.Handler` interface
2. **Path Parameters**: Uses `{name}` or `{name:pattern}` syntax
3. **Subrouters**: Create route groups with shared prefixes and middleware
4. **Middleware Support**: Via `Use()` method for chaining
5. **Route Matching**: Supports methods, hosts, schemes, and custom matchers
6. **Reverse Routing**: Generate URLs from route names and parameters

## Core Types
- `Router`: Main router implementing `http.Handler`
- `Route`: Represents a single route with matchers
- `Vars()`: Extracts path parameters from request context
- `Middleware`: Functions that wrap `http.Handler`
```