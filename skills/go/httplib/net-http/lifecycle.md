# net/http — Lifecycle

## Initialization

1. Create the `ServeMux` and register routes
2. Wrap with middleware if needed
3. Configure `http.Server` with timeouts
4. Optionally configure TLS with `srv.ListenAndServeTLS(certFile, keyFile)`

## Request Lifecycle

1. **Connection accepted** — goroutine spawned to handle the connection
2. **Headers parsed** — limited by `ReadHeaderTimeout` and `MaxHeaderBytes`
3. **Request body available** — via `r.Body` (streaming, read on demand)
4. **Handler called** — `ServeHTTP(w, r)` dispatched by `ServeMux`
5. **Response written** — headers must be set before body; `WriteHeader` called implicitly on first `Write`
6. **Body drained and closed** — server drains remaining body after handler returns
7. **Connection reused** — if `Connection: keep-alive` (default in HTTP/1.1)

## Shutdown

- `srv.Shutdown(ctx)` — gracefully stops accepting new connections, waits for active ones to complete
- `srv.Close()` — immediately closes all connections without waiting
- `srv.RegisterOnShutdown(callback)` — register cleanup callbacks (close DB connections etc.)

```go
srv.RegisterOnShutdown(func() {
    db.Close()
    cache.Close()
})
```
