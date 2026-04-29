# Quickstart

```markdown
# Quickstart Guide for gorilla/mux

## Installation
```bash
go get -u github.com/gorilla/mux
```

## Basic Router Setup
```go
package main

import (
    "fmt"
    "net/http"
    "github.com/gorilla/mux"
)

func main() {
    r := mux.NewRouter()
    r.HandleFunc("/", HomeHandler)
    http.ListenAndServe(":8080", r)
}

func HomeHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello, World!")
}
```

## Path Parameters
```go
r := mux.NewRouter()
r.HandleFunc("/users/{id}", GetUserHandler)
r.HandleFunc("/articles/{category}/{id:[0-9]+}", GetArticleHandler)

func GetUserHandler(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    id := vars["id"]
    fmt.Fprintf(w, "User ID: %s", id)
}
```

## Query Parameters
```go
r := mux.NewRouter()
r.HandleFunc("/search", SearchHandler)

func SearchHandler(w http.ResponseWriter, r *http.Request) {
    query := r.URL.Query()
    q := query.Get("q")
    page := query.Get("page")
    fmt.Fprintf(w, "Search: %s, Page: %s", q, page)
}
```

## Subrouters
```go
r := mux.NewRouter()
api := r.PathPrefix("/api/v1").Subrouter()
api.HandleFunc("/users", ListUsersHandler).Methods("GET")
api.HandleFunc("/users", CreateUserHandler).Methods("POST")
api.HandleFunc("/users/{id}", GetUserHandler).Methods("GET")
```

## Middleware
```go
r := mux.NewRouter()
r.Use(loggingMiddleware)
r.HandleFunc("/", HomeHandler)

func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        fmt.Printf("Request: %s %s\n", r.Method, r.URL.Path)
        next.ServeHTTP(w, r)
    })
}
```

## Route Groups with Common Middleware
```go
r := mux.NewRouter()
admin := r.PathPrefix("/admin").Subrouter()
admin.Use(authMiddleware)
admin.HandleFunc("/dashboard", DashboardHandler)
admin.HandleFunc("/settings", SettingsHandler)
```

## CORS Headers
```go
r := mux.NewRouter()
r.Use(corsMiddleware)

func corsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Access-Control-Allow-Origin", "*")
        w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
        if r.Method == "OPTIONS" {
            w.WriteHeader(http.StatusOK)
            return
        }
        next.ServeHTTP(w, r)
    })
}
```
```