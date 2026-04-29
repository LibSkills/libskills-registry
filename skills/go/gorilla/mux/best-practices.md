# Best Practices

```markdown
# Best Practices for gorilla/mux

## 1. Organize Routes by Domain
```go
// routes/users.go
func RegisterUserRoutes(r *mux.Router) {
    users := r.PathPrefix("/users").Subrouter()
    users.HandleFunc("", ListUsersHandler).Methods("GET")
    users.HandleFunc("", CreateUserHandler).Methods("POST")
    users.HandleFunc("/{id:[0-9]+}", GetUserHandler).Methods("GET")
    users.HandleFunc("/{id:[0-9]+}", UpdateUserHandler).Methods("PUT")
    users.HandleFunc("/{id:[0-9]+}", DeleteUserHandler).Methods("DELETE")
}

// main.go
func main() {
    r := mux.NewRouter()
    RegisterUserRoutes(r)
    RegisterArticleRoutes(r)
    http.ListenAndServe(":8080", r)
}
```

## 2. Use Named Routes for Reverse Routing
```go
r := mux.NewRouter()
r.HandleFunc("/users/{id}", GetUserHandler).Name("get_user")

// Generate URL from route name
func generateUserURL(id string) string {
    url, _ := r.Get("get_user").URL("id", id)
    return url.String()
}
```

## 3. Implement Proper Error Handling Middleware
```go
func errorHandler(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                log.Printf("Panic: %v", err)
                http.Error(w, "Internal Server Error", http.StatusInternalServerError)
            }
        }()
        next.ServeHTTP(w, r)
    })
}

r := mux.NewRouter()
r.Use(errorHandler)
```

## 4. Use Request Context for Request-Scoped Data
```go
type contextKey string
const userIDKey contextKey = "userID"

func authMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Authenticate and set user ID in context
        ctx := context.WithValue(r.Context(), userIDKey, "123")
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

func handler(w http.ResponseWriter, r *http.Request) {
    userID := r.Context().Value(userIDKey).(string)
    // Use userID safely
}
```

## 5. Version Your API Routes
```go
func RegisterV1Routes(r *mux.Router) {
    v1 := r.PathPrefix("/api/v1").Subrouter()
    v1.HandleFunc("/users", ListUsersV1Handler)
}

func RegisterV2Routes(r *mux.Router) {
    v2 := r.PathPrefix("/api/v2").Subrouter()
    v2.HandleFunc("/users", ListUsersV2Handler)
}
```

## 6. Use Custom Matchers for Complex Routing
```go
func hostMatcher(host string) mux.MatcherFunc {
    return func(r *http.Request, rm *mux.RouteMatch) bool {
        return r.Host == host
    }
}

r := mux.NewRouter()
r.MatcherFunc(hostMatcher("api.example.com")).Handler(apiHandler)
r.MatcherFunc(hostMatcher("www.example.com")).Handler(webHandler)
```
```