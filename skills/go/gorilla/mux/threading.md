# Threading

```markdown
# Thread Safety in gorilla/mux

## Thread Safety Guarantees
```go
// mux.Router is NOT safe for concurrent modification
// It IS safe for concurrent reads after configuration

// Safe: Concurrent requests to the same router
r := mux.NewRouter()
r.HandleFunc("/", HomeHandler)
go http.ListenAndServe(":8080", r) // Multiple goroutines can serve
go http.ListenAndServe(":8081", r) // Same router, different ports

// UNSAFE: Modifying router while serving
r := mux.NewRouter()
go http.ListenAndServe(":8080", r)
r.HandleFunc("/new", NewHandler) // Race condition!
```

## Concurrent Access Patterns

### 1. Read-Only Access (Safe)
```go
r := mux.NewRouter()
r.HandleFunc("/users", ListUsersHandler)
r.HandleFunc("/users/{id}", GetUserHandler)

// Multiple goroutines can serve requests concurrently
for i := 0; i < 10; i++ {
    go func() {
        http.ListenAndServe(fmt.Sprintf(":%d", 8080+i), r)
    }()
}
```

### 2. Dynamic Route Registration (Unsafe)
```go
// UNSAFE: Modifying router from multiple goroutines
r := mux.NewRouter()
for i := 0; i < 100; i++ {
    go func(id int) {
        r.HandleFunc(fmt.Sprintf("/route/%d", id), handler) // Race!
    }(i)
}
```

### 3. Safe Dynamic Registration with Mutex
```go
type SafeRouter struct {
    mu     sync.RWMutex
    router *mux.Router
}

func NewSafeRouter() *SafeRouter {
    return &SafeRouter{
        router: mux.NewRouter(),
    }
}

func (sr *SafeRouter) HandleFunc(pattern string, handler func(http.ResponseWriter, *http.Request)) *mux.Route {
    sr.mu.Lock()
    defer sr.mu.Unlock()
    return sr.router.HandleFunc(pattern, handler)
}

func (sr *SafeRouter) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    sr.mu.RLock()
    defer sr.mu.RUnlock()
    sr.router.ServeHTTP(w, r)
}
```

### 4. Thread-Safe Middleware State
```go
// UNSAFE: Shared state without synchronization
var requestCount int

func countingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        requestCount++ // Race condition!
        next.ServeHTTP(w, r)
    })
}

// SAFE: Use atomic operations
var requestCount int64

func safeCountingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        atomic.AddInt64(&requestCount, 1)
        next.ServeHTTP(w, r)
    })
}
```

### 5. Context-Based Thread Safety
```go
// Each request gets its own context (safe for concurrent access)
func handler(w http.ResponseWriter, r *http.Request) {
    // Context is request-scoped and safe
    ctx := r.Context()
    
    // Store request-specific data
    ctx = context.WithValue(ctx, "requestID", generateID())
    
    // Pass to other handlers
    nextHandler(w, r.WithContext(ctx))
}

// Accessing context from multiple goroutines (safe)
func processRequest(ctx context.Context) {
    go func() {
        select {
        case <-ctx.Done():
            // Context cancelled
        case result := <-doWork():
            // Process result
        }
    }()
}
```

## Best Practices for Concurrent Use
```go
// 1. Configure router completely before serving
r := mux.NewRouter()
r.HandleFunc("/", HomeHandler)
r.Use(middleware)
// All configuration done

// 2. Start serving
go http.ListenAndServe(":8080", r)

// 3. Never modify router after serving starts
// If dynamic routes are needed, use a proxy pattern
type DynamicRouter struct {
    mu     sync.RWMutex
    router *mux.Router
}

func (dr *DynamicRouter) AddRoute(pattern string, handler http.HandlerFunc) {
    dr.mu.Lock()
    defer dr.mu.Unlock()
    dr.router.HandleFunc(pattern, handler)
}

func (dr *DynamicRouter) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    dr.mu.RLock()
    defer dr.mu.RUnlock()
    dr.router.ServeHTTP(w, r)
}
```
```