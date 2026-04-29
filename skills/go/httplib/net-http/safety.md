# net/http — Safety

Red lines — conditions that must NEVER occur.

## NEVER start an HTTP server without ReadTimeout and WriteTimeout

Without these timeouts, a slow client can hold a connection open indefinitely, consuming goroutines and memory until the server runs out of resources.

```go
// NEVER
srv := &http.Server{Addr: ":8080", Handler: mux} // ❌ no timeouts
srv.ListenAndServe()

// ALWAYS: set timeouts
srv := &http.Server{
    Addr:         ":8080",
    Handler:      mux,
    ReadTimeout:  10 * time.Second,  // max time to read request
    WriteTimeout: 15 * time.Second,  // max time to write response
    IdleTimeout:  60 * time.Second,  // max idle time for keep-alive
}
```

## NEVER use `http.DefaultClient` or `http.DefaultTransport` in production

Default client has no timeout — requests hang forever when the remote server is slow or down. Default transport has no connection limits and leaks connections on body read errors.

```go
// NEVER — no timeout, connections can leak
resp, err := http.Get("https://api.example.com")

// ALWAYS: create a configured client
client := &http.Client{
    Timeout: 30 * time.Second,
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
    },
}
```

## NEVER call `w.WriteHeader()` after writing to the response

The first call to `w.Write()` implicitly calls `w.WriteHeader(http.StatusOK)`. Calling `w.WriteHeader()` afterward logs a warning and is ignored, silently producing the wrong status code.

```go
// NEVER — 200 is already sent
w.Write([]byte("data"))
w.WriteHeader(http.StatusNotFound) // ❌ ignored, client sees 200

// ALWAYS: set status before body
w.WriteHeader(http.StatusNotFound)
w.Write([]byte("not found"))
```

## NEVER forget to close response bodies

Every `http.Get()` or `client.Do()` that returns a non-nil response must have its body closed. Failure means the underlying TCP connection is not returned to the connection pool, gradually exhausting available connections.

```go
// NEVER — connection leaked
resp, _ := http.Get(url)
body, _ := io.ReadAll(resp.Body)
// return body — ❌ resp.Body.Close() never called

// ALWAYS: defer close immediately after checking error
resp, err := http.Get(url)
if err != nil {
    return nil, err
}
defer resp.Body.Close()
body, _ := io.ReadAll(resp.Body)

// ALWAYS: close even when you don't read
resp, _ := client.Do(req)
resp.Body.Close() // ✅ close immediately
```

## NEVER trust user-supplied paths for file serving

Using user input directly in `http.ServeFile` or `os.Open` without sanitization enables path traversal attacks.

```go
// NEVER — path traversal: /../../etc/passwd
filename := r.URL.Query().Get("file")
http.ServeFile(w, r, "./uploads/"+filename) // ❌

// ALWAYS: validate and sanitize
filename := path.Base(r.URL.Query().Get("file"))           // strip directory components
if filename == "." || filename == "/" {
    http.Error(w, "invalid path", http.StatusBadRequest)
    return
}
http.ServeFile(w, r, filepath.Join("./uploads", filename)) // ✅ safe join

// ALWAYS PREFERRED: use http.FileServer with a FileSystem
mux.Handle("/uploads/", http.StripPrefix("/uploads/",
    http.FileServer(http.Dir("./uploads"))))
```

## NEVER write to the response in a goroutine without synchronization

`http.ResponseWriter` is not goroutine-safe. Writing from multiple goroutines causes corrupted responses.

```go
// NEVER — race condition on ResponseWriter
func handler(w http.ResponseWriter, r *http.Request) {
    go func() {
        w.Write([]byte("async data")) // ❌ race with main handler
    }()
    w.Write([]byte("main data"))
}

// ALWAYS: collect results, write in handler
func handler(w http.ResponseWriter, r *http.Request) {
    resultCh := make(chan []byte)
    go func() {
        resultCh <- fetchData()
    }()
    data := <-resultCh
    w.Write(data)
}
```
