# Performance

```markdown
# Performance Characteristics of gorilla/mux

## Routing Performance
```go
// gorilla/mux uses a tree-based routing algorithm
// Performance characteristics:
// - O(n) for route registration
// - O(log n) for route matching (with tree structure)
// - Higher overhead than httprouter for simple routes

// Benchmark comparison (approximate):
// gorilla/mux: ~500ns per route match
// httprouter: ~100ns per route match
// chi: ~200ns per route match
```

## Memory Allocation Patterns
```go
// Each request creates new Vars map
func handler(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r) // Allocates map[string]string
    // Use vars
}

// To reduce allocations, cache Vars when possible
var varsCache sync.Map

func cachedHandler(w http.ResponseWriter, r *http.Request) {
    key := r.URL.Path
    if cached, ok := varsCache.Load(key); ok {
        vars := cached.(map[string]string)
        // Use cached vars
        return
    }
    vars := mux.Vars(r)
    varsCache.Store(key, vars)
}
```

## Optimization Tips

### 1. Use Specific Route Patterns
```go
// BAD: Generic patterns cause more matching work
r.HandleFunc("/{resource}/{id}", GenericHandler)

// GOOD: Specific patterns match faster
r.HandleFunc("/users/{id:[0-9]+}", UserHandler)
r.HandleFunc("/products/{id:[0-9]+}", ProductHandler)
```

### 2. Minimize Middleware Chain
```go
// BAD: Too many middleware layers
r.Use(middleware1)
r.Use(middleware2)
r.Use(middleware3)
r.Use(middleware4)
r.Use(middleware5)

// GOOD: Combine middleware when possible
r.Use(func(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        middleware1(w, r, func() {
            middleware2(w, r, func() {
                next.ServeHTTP(w, r)
            })
        })
    })
})
```

### 3. Use PathPrefix for Static Routes
```go
// BAD: Individual route registration
r.HandleFunc("/static/css/style.css", StaticHandler)
r.HandleFunc("/static/js/app.js", StaticHandler)

// GOOD: Use PathPrefix for static files
r.PathPrefix("/static/").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))
```

### 4. Avoid Regex in Hot Paths
```go
// BAD: Complex regex in frequently accessed routes
r.HandleFunc("/items/{id:[a-zA-Z0-9_-]+}", ItemHandler)

// GOOD: Simple validation in handler
r.HandleFunc("/items/{id}", ItemHandler)
// Validate in handler
func ItemHandler(w http.ResponseWriter, r *http.Request) {
    id := mux.Vars(r)["id"]
    if !isValidID(id) {
        http.Error(w, "Invalid ID", http.StatusBadRequest)
        return
    }
}
```

## Memory Pool for Vars
```go
var varsPool = sync.Pool{
    New: func() interface{} {
        return make(map[string]string)
    },
}

func poolHandler(w http.ResponseWriter, r *http.Request) {
    vars := varsPool.Get().(map[string]string)
    defer varsPool.Put(vars)
    
    // Populate vars from request
    for k, v := range mux.Vars(r) {
        vars[k] = v
    }
    // Use vars
}
```
```