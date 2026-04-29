# net/http — Pitfalls

Common mistakes that cause resource leaks, broken responses, or production outages.

## Not closing the response body (connection pool leak)

The most common net/http mistake. Forgetting `resp.Body.Close()` leaks connections in the transport pool.

```go
// BAD: body never closed — connection stays open
resp, err := http.Get("https://api.example.com/data")
if err != nil {
    return err
}
body, _ := io.ReadAll(resp.Body) // ❌ Body.Close() never called

// GOOD: always close, even on errors
resp, err := http.Get("https://api.example.com/data")
if err != nil {
    return err
}
defer resp.Body.Close()
body, _ := io.ReadAll(resp.Body)

// GOOD: close even when not reading the body
resp, err := http.Post(url, "application/json", body)
if err != nil {
    return err
}
resp.Body.Close() // ✅ close immediately if you don't need the response
```

## Reading request body multiple times

Request body is a stream — reading it consumes it. Subsequent reads get empty data.

```go
// BAD: body consumed by first read
func handler(w http.ResponseWriter, r *http.Request) {
    body1, _ := io.ReadAll(r.Body)   // consumes body
    log.Printf("body: %s", body1)

    body2, _ := io.ReadAll(r.Body)   // ❌ empty, already consumed
    process(body2)
}

// GOOD: replace body after reading
func handler(w http.ResponseWriter, r *http.Request) {
    body, _ := io.ReadAll(r.Body)
    r.Body = io.NopCloser(bytes.NewBuffer(body)) // ✅ restore for downstream

    body2, _ := io.ReadAll(r.Body)   // works
    process(body2)
}

// GOOD: read once, save reference
func handler(w http.ResponseWriter, r *http.Request) {
    body, _ := io.ReadAll(r.Body)
    r.Body.Close()
    // use 'body', no more reads from r.Body
}
```

## ServeMux path pattern conflicts (Go 1.22+)

Go 1.22+ strict routing can cause conflicts the compiler cannot catch until runtime.

```go
// BAD: these two patterns conflict
mux.HandleFunc("GET /api/users/{id}", handler1)    // matches /api/users/123
mux.HandleFunc("GET /api/users/new", handler2)     // ❌ conflict: both match /api/users/new

// GOOD: use a wildcard suffix or restructure
mux.HandleFunc("GET /api/users/{id}", handler1)     // matches /api/users/123
mux.HandleFunc("GET /api/users/new{$}", handler2)   // ✅ {$} is exact match only
```

## No default timeouts on server or client

The zero-value `http.Server` and `http.Client` have no timeouts — a slow client can hold connections forever.

```go
// BAD: no timeouts
srv := &http.Server{Addr: ":8080", Handler: mux} // ❌ no ReadTimeout, WriteTimeout
srv.ListenAndServe()

// GOOD: always set timeouts
srv := &http.Server{
    Addr:         ":8080",
    Handler:      mux,
    ReadTimeout:  10 * time.Second,
    WriteTimeout: 15 * time.Second,
    IdleTimeout:  60 * time.Second,
}

// BAD: default client has no timeout
client := &http.Client{} // ❌ requests can hang forever

// GOOD: set a timeout
client := &http.Client{Timeout: 30 * time.Second}
```

## Writing to the response after already writing the header

Writing to `http.ResponseWriter` implicitly calls `WriteHeader(http.StatusOK)` the first time. Subsequent writes succeed but header changes are ignored.

```go
// BAD: status code set but ignored
func handler(w http.ResponseWriter, r *http.Request) {
    w.Write([]byte("partial"))       // implicitly sets 200
    w.WriteHeader(http.StatusOK)     // ❌ ignored — already wrote
    w.Write([]byte("data"))
}

// GOOD: set status before writing body
func handler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)     // ✅ must come before Write
    w.Write([]byte(`{"status":"ok"}`))
}

// GOOD: use Write for 200 responses
func handler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(data)  // ✅ implicitly calls WriteHeader(200)
}
```

## Double WriteHeader call

Calling `http.Error` or `w.WriteHeader` twice produces a logged warning and the second call is silently ignored.

```go
// BAD: double WriteHeader
func handler(w http.ResponseWriter, r *http.Request) {
    if err := validate(r); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    http.Error(w, "not found", http.StatusNotFound) // ❌ never reached if return present
}

// BAD (subtle): missing return after http.Error
func auth(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if r.Header.Get("Token") == "" {
            http.Error(w, "unauthorized", http.StatusUnauthorized) // ❌ writes 401
            // ❌ MISSING return — next handler also runs and writes 200!
        }
        next.ServeHTTP(w, r)
    })
}

// GOOD: always return after writing error responses
func auth(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if r.Header.Get("Token") == "" {
            http.Error(w, "unauthorized", http.StatusUnauthorized)
            return // ✅ prevents next handler from running
        }
        next.ServeHTTP(w, r)
    })
}
```

## Using the default HTTP client in production

`http.DefaultClient` has no timeout and uses `http.DefaultTransport` with default settings.

```go
// BAD: production code using default client
resp, err := http.Get("https://api.example.com") // ❌ uses http.DefaultClient
if err != nil {
    log.Fatal(err)
}
defer resp.Body.Close()

// GOOD: explicit client with configured transport
var httpClient = &http.Client{
    Timeout: 30 * time.Second,
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
    },
}
resp, err := httpClient.Get("https://api.example.com")
```

## Not handling errors from `r.Body.Close()`

`r.Body.Close()` returns an error, especially when the body wasn't fully read. Ignoring it may silently swallow read errors.

```go
// BAD: ignoring close error
defer r.Body.Close()

// GOOD: check close error
defer func() {
    if err := r.Body.Close(); err != nil {
        log.Printf("error closing body: %v", err)
    }
}()

// GOOD: can't read body but want to drain — use io.Copy(io.Discard, r.Body) first
defer func() {
    io.Copy(io.Discard, r.Body) // drain remaining
    r.Body.Close()
}()
```
