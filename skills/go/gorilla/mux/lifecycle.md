# Lifecycle

```markdown
# Lifecycle Management for gorilla/mux

## Construction
```go
// Basic construction
r := mux.NewRouter()

// With options
r := mux.NewRouter()
r.StrictSlash(true)
r.SkipClean(true)
r.UseEncodedPath() // Use encoded paths for matching
```

## Route Registration
```go
// Routes can be registered at any time before serving
r := mux.NewRouter()
r.HandleFunc("/users", ListUsersHandler)
r.HandleFunc("/users/{id}", GetUserHandler)

// Routes can be added dynamically (but not recommended)
go func() {
    time.Sleep(5 * time.Second)
    r.HandleFunc("/new-feature", NewFeatureHandler) // Works but risky
}()
```

## Destruction and Cleanup
```go
// Router doesn't have explicit cleanup, but middleware can handle resources
func cleanupMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Setup
        db := getDBConnection()
        defer db.Close() // Cleanup after request
        
        // Store in context
        ctx := context.WithValue(r.Context(), "db", db)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

## Resource Management Patterns
```go
// Proper resource cleanup with middleware
type Server struct {
    router *mux.Router
    db     *sql.DB
    cache  *redis.Client
}

func NewServer() *Server {
    s := &Server{
        router: mux.NewRouter(),
        db:     initDB(),
        cache:  initCache(),
    }
    s.registerRoutes()
    return s
}

func (s *Server) Close() error {
    if err := s.db.Close(); err != nil {
        return err
    }
    if err := s.cache.Close(); err != nil {
        return err
    }
    return nil
}

func (s *Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    s.router.ServeHTTP(w, r)
}
```

## Graceful Shutdown
```go
func main() {
    r := mux.NewRouter()
    r.HandleFunc("/", HomeHandler)
    
    srv := &http.Server{
        Addr:    ":8080",
        Handler: r,
    }
    
    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("listen: %s\n", err)
        }
    }()
    
    // Wait for interrupt signal
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit
    
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    if err := srv.Shutdown(ctx); err != nil {
        log.Fatal("Server forced to shutdown:", err)
    }
}
```
```