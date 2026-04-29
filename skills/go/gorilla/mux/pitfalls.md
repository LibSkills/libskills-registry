# Pitfalls

```markdown
# Common Pitfalls with gorilla/mux

## 1. Forgetting to Use mux.Vars()
**BAD**: Accessing path parameters directly from URL
```go
r.HandleFunc("/users/{id}", func(w http.ResponseWriter, r *http.Request) {
    id := r.URL.Query().Get("id") // Wrong! This gets query params
    fmt.Fprintf(w, "User: %s", id)
})
```

**GOOD**: Using mux.Vars() to extract path parameters
```go
r.HandleFunc("/users/{id}", func(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    id := vars["id"] // Correctly gets path parameter
    fmt.Fprintf(w, "User: %s", id)
})
```

## 2. Not Specifying HTTP Methods
**BAD**: Route matches all methods
```go
r.HandleFunc("/users", UserHandler) // Matches GET, POST, PUT, DELETE
```

**GOOD**: Restrict to specific methods
```go
r.HandleFunc("/users", ListUsersHandler).Methods("GET")
r.HandleFunc("/users", CreateUserHandler).Methods("POST")
```

## 3. Overlapping Routes
**BAD**: Ambiguous route patterns
```go
r.HandleFunc("/users/{id}", GetUserHandler)
r.HandleFunc("/users/new", NewUserHandler) // Never matches!
```

**GOOD**: Order specific routes first
```go
r.HandleFunc("/users/new", NewUserHandler) // Specific route first
r.HandleFunc("/users/{id}", GetUserHandler) // Then parameterized
```

## 4. Missing Regex Constraints
**BAD**: Accepting invalid parameter values
```go
r.HandleFunc("/articles/{id}", GetArticleHandler) // Accepts "abc" as ID
```

**GOOD**: Constrain with regex
```go
r.HandleFunc("/articles/{id:[0-9]+}", GetArticleHandler) // Only digits
```

## 5. Incorrect Subrouter Usage
**BAD**: Not using PathPrefix for subrouters
```go
api := r.PathPrefix("/api/v1").Subrouter()
api.HandleFunc("/api/v1/users", ListUsersHandler) // Redundant prefix
```

**GOOD**: Subrouter inherits prefix
```go
api := r.PathPrefix("/api/v1").Subrouter()
api.HandleFunc("/users", ListUsersHandler) // Becomes /api/v1/users
```

## 6. Forgetting to Handle 404s
**BAD**: No custom 404 handler
```go
r := mux.NewRouter()
r.HandleFunc("/", HomeHandler)
// Missing routes return default 404
```

**GOOD**: Custom 404 handler
```go
r := mux.NewRouter()
r.NotFoundHandler = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusNotFound)
    fmt.Fprintf(w, "Custom 404: %s not found", r.URL.Path)
})
```

## 7. Not Using StrictSlash
**BAD**: Inconsistent trailing slash behavior
```go
r := mux.NewRouter()
r.HandleFunc("/users", ListUsersHandler) // /users works, /users/ doesn't
```

**GOOD**: Use StrictSlash for consistency
```go
r := mux.NewRouter()
r.StrictSlash(true) // Redirect /users/ to /users
r.HandleFunc("/users", ListUsersHandler)
```

## 8. Ignoring Middleware Order
**BAD**: Middleware applied after routes
```go
r := mux.NewRouter()
r.HandleFunc("/", HomeHandler)
r.Use(loggingMiddleware) // Too late! Won't apply to HomeHandler
```

**GOOD**: Apply middleware before routes
```go
r := mux.NewRouter()
r.Use(loggingMiddleware) // Applied to all subsequent routes
r.HandleFunc("/", HomeHandler)
```
```