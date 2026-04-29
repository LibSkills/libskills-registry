# Safety

```markdown
# Safety Conditions for gorilla/mux

## Condition 1: NEVER Access mux.Vars() Without Checking Context
**BAD**: Assuming Vars always returns valid data
```go
func handler(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    id := vars["id"] // Panics if "id" doesn't exist
}
```

**GOOD**: Check for key existence
```go
func handler(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    id, ok := vars["id"]
    if !ok {
        http.Error(w, "Missing id parameter", http.StatusBadRequest)
        return
    }
    // Use id safely
}
```

## Condition 2: NEVER Use Unvalidated Path Parameters in SQL Queries
**BAD**: Direct injection of path parameters
```go
func handler(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    id := vars["id"]
    query := fmt.Sprintf("SELECT * FROM users WHERE id = %s", id) // SQL injection!
}
```

**GOOD**: Use parameterized queries
```go
func handler(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    id := vars["id"]
    // Validate and use parameterized query
    if !isValidID(id) {
        http.Error(w, "Invalid ID", http.StatusBadRequest)
        return
    }
    query := "SELECT * FROM users WHERE id = ?"
    db.Query(query, id)
}
```

## Condition 3: NEVER Share Router State Across Goroutines Without Synchronization
**BAD**: Modifying router after serving
```go
r := mux.NewRouter()
go http.ListenAndServe(":8080", r)
r.HandleFunc("/new", NewHandler) // Race condition!
```

**GOOD**: Configure router before serving
```go
r := mux.NewRouter()
r.HandleFunc("/new", NewHandler) // Configure first
go http.ListenAndServe(":8080", r) // Then serve
```

## Condition 4: NEVER Use Path Parameters Without Regex Constraints for Critical IDs
**BAD**: Accepting any string as ID
```go
r.HandleFunc("/users/{id}", handler) // Accepts "../../etc/passwd"
```

**GOOD**: Constrain with regex
```go
r.HandleFunc("/users/{id:[a-f0-9]{24}}", handler) // MongoDB ObjectID format
```

## Condition 5: NEVER Ignore Errors from ListenAndServe
**BAD**: Ignoring server errors
```go
http.ListenAndServe(":8080", r) // Error silently ignored
```

**GOOD**: Handle server errors
```go
if err := http.ListenAndServe(":8080", r); err != nil {
    log.Fatalf("Server failed: %v", err)
}
```
```