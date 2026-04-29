# net/http — Best Practices

## Server Configuration

- **Use `ReadHeaderTimeout` separately** from `ReadTimeout` to defend against slow-header attacks before reading the full request
- **Set `MaxHeaderBytes`** to a reasonable limit (default 1MB, consider 64KB for most APIs)
- **Use `ServerErrorLog`** to route server errors to your structured logger instead of stderr
- **Implement `BaseContext`** (Go 1.13+) to set a root context for all requests derived from the server

```go
srv := &http.Server{
    Addr:              ":8080",
    Handler:           mux,
    ReadHeaderTimeout: 5 * time.Second,
    ReadTimeout:       10 * time.Second,
    WriteTimeout:      15 * time.Second,
    IdleTimeout:       60 * time.Second,
    MaxHeaderBytes:    1 << 16, // 64KB
    ErrorLog:          log.New(logger.Writer(), "http: ", log.LstdFlags),
    BaseContext:       func(_ net.Listener) context.Context { return context.Background() },
}
```

## Client Best Practices

- **Reuse `http.Client`** across requests — creating clients per-request defeats connection pooling
- **Set `Timeout`** on the client, and per-request `context.WithTimeout` for finer control
- **Limit `MaxIdleConnsPerHost`** to prevent one host from consuming all idle connections
- **Set `DisableCompression: false`** (default) and let the client handle gzip transparently
- **Use `NewRequestWithContext`** instead of setting `req.Header` after creation

```go
client := &http.Client{
    Timeout: 30 * time.Second,
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
        TLSHandshakeTimeout: 10 * time.Second,
    },
}
```

## Middleware Chain Pattern

```go
// Chain multiple middleware
type middleware func(http.Handler) http.Handler

func chain(h http.Handler, mws ...middleware) http.Handler {
    for i := len(mws) - 1; i >= 0; i-- {
        h = mws[i](h)
    }
    return h
}

// Usage
handler := chain(
    myHandler,
    loggingMiddleware,
    authMiddleware,
    recoveryMiddleware,
)
```

## Graceful Shutdown

Always implement graceful shutdown in production services. See quickstart.md for the full pattern.

## Error Responses

Return consistent error responses:

```go
func writeJSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

func writeError(w http.ResponseWriter, status int, msg string) {
    writeJSON(w, status, map[string]string{"error": msg})
}
```

## Response Controller (Go 1.20+)

Use `ResponseController` to access Flusher or Hijacker:

```go
func handler(w http.ResponseWriter, r *http.Request) {
    ctrl := http.NewResponseController(w)
    // Flush mid-response
    w.Write([]byte("partial"))
    ctrl.Flush()
    // Set deadline for slow clients
    ctrl.SetWriteDeadline(time.Now().Add(30 * time.Second))
}
```
