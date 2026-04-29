# net/http — Threading & Concurrency

## Goroutine Model

Each incoming HTTP request runs in its own goroutine. Multiple requests are handled concurrently by default — no additional concurrency setup is needed.

```go
func handler(w http.ResponseWriter, r *http.Request) {
    // Each call runs in its own goroutine
    // w and r are safe within this handler
}
```

## Thread Safety

- **`http.ResponseWriter`** is NOT goroutine-safe — do not write to it from multiple goroutines
- **`*http.Request`** is safe to read from one goroutine but NOT safe to access concurrently
- **`http.ServeMux`** is safe for concurrent reads (route registration is NOT safe after `ListenAndServe`)
- **`http.Client`** is safe for concurrent use — share a single client across goroutines
- **`http.Transport`** is safe for concurrent use — the connection pool is internally synchronized

## Patterns

### Running background work per-request
```go
func handler(w http.ResponseWriter, r *http.Request) {
    resultCh := make(chan Result, 1)
    go func() {
        resultCh <- expensiveWork(r.Context())
    }()
    select {
    case result := <-resultCh:
        json.NewEncoder(w).Encode(result)
    case <-r.Context().Done():
        http.Error(w, "timeout", http.StatusGatewayTimeout)
    }
}
```

### Sharing a client across goroutines
```go
var httpClient = &http.Client{Timeout: 30 * time.Second}

func concurrentFetcher(urls []string) []Response {
    var wg sync.WaitGroup
    results := make([]Response, len(urls))
    for i, url := range urls {
        wg.Add(1)
        go func(i int, url string) {
            defer wg.Done()
            resp, err := httpClient.Get(url) // ✅ safe for concurrent use
            if err != nil {
                return
            }
            defer resp.Body.Close()
            body, _ := io.ReadAll(resp.Body)
            results[i] = Response{URL: url, Body: body}
        }(i, url)
    }
    wg.Wait()
    return results
}
```
