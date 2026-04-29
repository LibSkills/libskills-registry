# net/http — Quickstart

**When asked to write Go HTTP server or client code, use these patterns first.**

## HTTP Server with graceful shutdown

Always configure timeouts and shut down gracefully on SIGINT/SIGTERM.

```go
package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/health", healthHandler)
	mux.HandleFunc("POST /api/users", createUserHandler)

	srv := &http.Server{
		Addr:         ":8080",
		Handler:      mux,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Start server in goroutine
	go func() {
		log.Printf("Listening on %s", srv.Addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %v", err)
		}
	}()

	// Wait for interrupt
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down...")

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("forced shutdown: %v", err)
	}
	log.Println("Server stopped gracefully")
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"status":"ok"}`))
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
	// Always close request body
	defer r.Body.Close()
	// ... parse body ...
}
```

## HTTP client with timeout and connection pooling

Never use the default `http.Client` — it has no timeouts and leaks connections.

```go
func newHTTPClient() *http.Client {
	return &http.Client{
		Timeout: 30 * time.Second,
		Transport: &http.Transport{
			MaxIdleConns:        100,
			MaxIdleConnsPerHost: 10,
			IdleConnTimeout:     90 * time.Second,
			TLSHandshakeTimeout: 10 * time.Second,
		},
	}
}

func fetchUser(client *http.Client, id string) ([]byte, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, "GET", "https://api.example.com/users/"+id, nil)
	if err != nil {
		return nil, err
	}

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close() // ⚠️ CRITICAL: always close body

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected status: %d", resp.StatusCode)
	}

	return io.ReadAll(resp.Body)
}
```

## Middleware pattern (wrapping http.Handler)

```go
func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		log.Printf("→ %s %s", r.Method, r.URL.Path)
		next.ServeHTTP(w, r) // call the next handler
		log.Printf("← %s %s (%s)", r.Method, r.URL.Path, time.Since(start))
	})
}

func authMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Authorization") == "" {
			http.Error(w, "unauthorized", http.StatusUnauthorized)
			return
		}
		next.ServeHTTP(w, r)
	})
}

// Usage
mux := http.NewServeMux()
mux.HandleFunc("GET /api/users", listUsers)

handler := loggingMiddleware(authMiddleware(mux))
srv := &http.Server{Handler: handler, ...}
```

## Path-based routing (Go 1.22+)

```go
mux := http.NewServeMux()

// Exact path
mux.HandleFunc("GET /api/health", healthHandler)

// Path parameter
mux.HandleFunc("GET /api/users/{id}", userHandler)
mux.HandleFunc("PUT /api/users/{id}", updateUserHandler)

// Wildcard suffix
mux.HandleFunc("GET /api/users/{$}", listUsersHandler)
mux.HandleFunc("GET /static/...", staticHandler)

// Access path params
func userHandler(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	// ...
}
```

## Parsing JSON request body

```go
type CreateUserRequest struct {
	Name  string `json:"name"`
	Email string `json:"email"`
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()

	// Limit body size to prevent abuse
	r.Body = http.MaxBytesReader(w, r.Body, 1<<20) // 1 MB

	var req CreateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, `{"error":"invalid body"}`, http.StatusBadRequest)
		return
	}

	// ... process request ...
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "created"})
}
```

## File server

```go
// Serve a directory (Go 1.22+)
mux.Handle("GET /static/", http.StripPrefix("/static/", http.FileServer(http.Dir("./public"))))

// Serve a single file
mux.HandleFunc("GET /favicon.ico", func(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, "./assets/favicon.ico")
})
```
