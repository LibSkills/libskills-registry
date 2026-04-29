# Gin — Lifecycle

## Initialization

```go
import "github.com/gin-gonic/gin"

// Development mode (verbose)
gin.SetMode(gin.DebugMode)

// Production mode (silent, optimized)
gin.SetMode(gin.ReleaseMode)

// Test mode (no output)
gin.SetMode(gin.TestMode)

// Create router (no middleware)
r := gin.New()

// Or with default Logger + Recovery middleware
r := gin.Default()
```

## Route Registration

```go
// Match order matters — Gin matches in registration order
r.GET("/ping", pingHandler)
r.POST("/users", createUser)
r.GET("/users/:id", getUser)
r.PUT("/users/:id", updateUser)
r.DELETE("/users/:id", deleteUser)

// Groups
v1 := r.Group("/api/v1")
v1.Use(authMiddleware) // group-scoped middleware
{
    v1.GET("/users", listUsers)
    v1.POST("/users", createUser)
}

// Route params
r.GET("/users/:id/posts/:postId", func(c *gin.Context) {
    id := c.Param("id")
    postId := c.Param("postId")
})

// Query params
r.GET("/search", func(c *gin.Context) {
    q := c.Query("q")        // "" if missing
    page := c.DefaultQuery("page", "1")
})
```

## Request Lifecycle

```
Request arrives
    │
    ▼
[Global middleware] ← r.Use(...)
    │
    ▼
[Group middleware]  ← group.Use(...)
    │
    ▼
[Route handler]     ← runs handler function
    │
    ▼
[After hooks]       ← deferred cleanup, logging
    │
    ▼
Response sent
```

- Global middleware runs on every request
- Group middleware runs on routes in that group  
- Handlers call `c.Next()` to pass to next in chain
- Handlers call `c.Abort()` → `c.Next()` is skipped for remaining handlers

## Serving

```go
srv := &http.Server{
    Addr:    ":8080",
    Handler: r,
}

// Non-blocking
go srv.ListenAndServe()

// TLS
go srv.ListenAndServeTLS("cert.pem", "key.pem")
```

## Shutdown

```go
// Graceful shutdown with timeout
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
if err := srv.Shutdown(ctx); err != nil {
    log.Fatalf("server forced to shutdown: %v", err)
}
```

- `Shutdown()` stops accepting new connections
- In-flight requests have up to the context timeout to complete
- After timeout, `Close()` closes all connections immediately
- Always call `Shutdown()` on OS signal (SIGINT/SIGTERM)

## Engine Reuse

- One engine per process is standard
- DO NOT create engines dynamically per request — they are expensive
- DO NOT reuse the same engine across multiple `ListenAndServe` calls (port conflict)
