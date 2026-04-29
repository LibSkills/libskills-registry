# Gin — Threading

## Per-Request Goroutine Model

Gin uses Go's `net/http` server, which spawns a goroutine per incoming connection. This means:

- **Every request runs in its own goroutine** by default
- **No shared state between requests** unless explicitly shared (globals, DB pools, caches)
- **`*gin.Context` is NOT safe for concurrent access** — each handler gets its own

## Context Safety

| Operation | Safe across goroutines? | Notes |
|-----------|------------------------|-------|
| `c.Get()` / `c.Set()` | No | Only call from the handler goroutine |
| `c.JSON()` / `c.String()` | No | Only call from the handler goroutine |
| `c.Request.Body` | No | Not safe once handler returns |
| `c.Copy()` | Yes | Returns a read-only snapshot |
| Values extracted before goroutine | Yes | Standard Go value safety |

## Middleware in Goroutines

Middleware runs in the same goroutine as the handler. `c.Next()` is synchronous — it blocks until the next handler returns.

```go
func timingMiddleware(c *gin.Context) {
    start := time.Now()
    c.Next() // blocks until handler + subsequent middleware finish
    log.Printf("Request took %v", time.Since(start))
}
```

## Shared State (DB, Cache, Config)

These are safe if they implement their own synchronization:

```go
var db *sql.DB     // sql.DB is goroutine-safe
var cache *redis.Client // redis client is goroutine-safe
var cfg config.Config   // read-only after init

func handler(c *gin.Context) {
    rows, _ := db.QueryContext(c.Request.Context(), "SELECT ...")
    // db.QueryContext is safe to call concurrently
}
```

## Async Work Inside Handlers

When spawning goroutines from a handler:

```go
func handler(c *gin.Context) {
    userID := c.GetString("user_id") // extract before goroutine

    go func() {
        result := expensiveComputation(userID)
        // Do NOT touch c here — context is recycled
        // Send result through a channel, callback, or message queue
        notifyResult(result)
    }()

    c.JSON(202, gin.H{"status": "accepted"})
}
```

## Rate Limiting and Throttling

Use sync primitives for application-level throttling:

```go
var limiter = rate.NewLimiter(rate.Limit(100), 200)

func rateLimit(c *gin.Context) {
    if !limiter.Allow() {
        c.AbortWithStatusJSON(429, gin.H{"error": "rate limit exceeded"})
        return
    }
    c.Next()
}
```

The `rate.Limiter` is goroutine-safe. But custom buckets must use `sync.Mutex` or `sync.RWMutex`.
