# net/http — Performance

## Connection Pool Tuning

The default `http.Transport` is well-tuned for most workloads. Adjust these when benchmarks indicate a bottleneck:

```go
transport := &http.Transport{
    // Connection limits
    MaxIdleConns:        100,            // total idle connections
    MaxIdleConnsPerHost: 10,             // per-host limit
    MaxConnsPerHost:     0,              // unlimited (set if needed)
    IdleConnTimeout:     90 * time.Second,

    // Timeouts
    TLSHandshakeTimeout:   10 * time.Second,
    ResponseHeaderTimeout: 10 * time.Second,
    ExpectContinueTimeout: 1 * time.Second,
}
```

## Key Performance Tips

- **Reuse `http.Client`** — never create one per request
- **Prefer `json.NewEncoder(w)`** over `json.Marshal(w.Write(...))` — avoids allocating a byte slice
- **Use `sync.Pool`** for frequently allocated structs (like request/response objects)
- **Set `DisableKeepAlives: false`** (default) — keeps connections alive for reuse
- **For high throughput**, consider increasing `GOMAXPROCS` and using `http.Server.ReadTimeout` to prevent slow clients from occupying goroutines
- **Profile first** before tuning — use `pprof` to identify actual bottlenecks

## Server-Sent Events (SSE)

For streaming, use `http.Flusher`:

```go
func sseHandler(w http.ResponseWriter, r *http.Request) {
    flusher, ok := w.(http.Flusher)
    if !ok {
        http.Error(w, "streaming unsupported", http.StatusInternalServerError)
        return
    }
    w.Header().Set("Content-Type", "text/event-stream")
    for {
        fmt.Fprintf(w, "data: %s\n\n", time.Now().String())
        flusher.Flush()
        time.Sleep(1 * time.Second)
    }
}
```

## Benchmark Context

- net/http handles ~50K-100K requests/second on modern hardware with proper tuning
- Default ServeMux routing uses linear scan in Go < 1.22 — replace with custom radix tree or framework for 500+ routes
