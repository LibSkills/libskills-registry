# Gin — Performance

## Throughput (approximate, modern x86_64)

| Mode | Requests/sec | Notes |
|------|-------------|-------|
| Gin (Release), zero middleware | ~3-4M/s | Radix tree router |
| Gin + Logger + Recovery | ~2.5-3M/s | Minimal overhead |
| Gin + 3 middleware + body bind | ~1-2M/s | Binding adds allocation cost |
| Gin + body bind + DB query | Depends on DB | Network-bound at this point |

## Performance Rules

- **Always use `gin.ReleaseMode` in production**: Debug mode logs every request and disables some optimizations
- **Avoid reflection-heavy binds on every request**: Pre-bind validation rules or use raw `c.GetRawData()` for custom parsing
- **Pre-allocate response slices**: When returning lists, pre-allocate the slice if you know the size
- **Use `c.Writer.Write()` for large binary responses** instead of marshaling and returning gin.H
- **Group middleware by scope**: Don't apply DB-connection middleware to health-check routes

## Router Performance

```go
// FAST: static routes are O(1) hash lookups
r.GET("/health", healthHandler)

// FAST: parameterized routes are O(path-length) tree traversal
r.GET("/users/:id", userHandler)

// SLOW: catch-all routes re-evaluate every request
r.GET("/*path", catchAllHandler)

// SLOW: too many conflicting param routes (radix tree splits paths)
r.GET("/:resource/:id", handler1)   // two params
r.GET("/:resource/stats", handler2) // second segment switches from param to static
```

## Memory and Allocation

```go
// BAD: allocates gin.H map on every request
func handler(c *gin.Context) {
    c.JSON(200, gin.H{
        "status": "ok",
        "data":   gin.H{"name": name, "age": age}, // nested maps
    })
}

// GOOD: use typed structs (escape analysis is friendlier)
type Response struct {
    Status string `json:"status"`
    Data   User   `json:"data"`
}
func handler(c *gin.Context) {
    c.JSON(200, Response{Status: "ok", Data: user})
}
```

## Body Size Limits

```go
// Limit request body to 1MB (prevents memory exhaustion)
r.MaxMultipartMemory = 8 << 20 // 8MB for multipart
func handler(c *gin.Context) {
    c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, 1<<20)
}
```

## Profiling

```go
import "net/http/pprof"

// Register pprof routes (only in debug builds)
func registerPprof(r *gin.Engine) {
    r.GET("/debug/pprof/*any", gin.WrapH(http.DefaultServeMux))
}
```
