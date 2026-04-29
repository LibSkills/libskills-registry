# Gin — Pitfalls

Common mistakes that cause crashes, data races, or silent misbehavior.

## Do NOT capture `*gin.Context` in a goroutine without calling `c.Copy()`

Gin reuses `*gin.Context` from a sync.Pool after the handler returns. Accessing it in a goroutine is a data race.

```go
// BAD: data race — context reused after handler returns
func handler(c *gin.Context) {
    go func() {
        log.Println(c.GetString("user")) // ❌ races with pool reuse
    }()
    c.JSON(200, gin.H{"status": "ok"})
}

// GOOD: copy the context first
func handler(c *gin.Context) {
    user := c.GetString("user")          // extract what you need
    go func() {
        log.Println(user)
    }()
    c.JSON(200, gin.H{"status": "ok"})
}

// OR: use c.Copy() (creates a snapshot)
func handler(c *gin.Context) {
    cc := c.Copy()
    go func() {
        log.Println(cc.GetString("user"))
    }()
    c.JSON(200, gin.H{"status": "ok"})
}
```

## Do NOT write to the response after calling `c.Abort()`

`Abort()` prevents subsequent handlers from running but does NOT halt the current handler. Writing the response twice causes a connection error.

```go
// BAD: double response write
func authMiddleware(c *gin.Context) {
    token := c.GetHeader("Authorization")
    if token == "" {
        c.AbortWithStatusJSON(401, gin.H{"error": "no token"})
        return // ❌ MISSING return — handler below still runs!
    }
    c.Next()
}

// GOOD: always return after abort
func authMiddleware(c *gin.Context) {
    token := c.GetHeader("Authorization")
    if token == "" {
        c.AbortWithStatusJSON(401, gin.H{"error": "no token"})
        return // ✅ stops execution
    }
    c.Next()
}
```

## Do NOT use `c.Request.Body` directly without replacing it

Gin reads the body once. If you read it in middleware, the handler gets an empty body. Always replace the body reader.

```go
// BAD: body consumed, handler gets nothing
func logBody(c *gin.Context) {
    body, _ := io.ReadAll(c.Request.Body) // ❌ body consumed
    log.Println(string(body))
    c.Next()
}

// GOOD: replace the body after reading
func logBody(c *gin.Context) {
    body, _ := io.ReadAll(c.Request.Body)
    c.Request.Body = io.NopCloser(bytes.NewBuffer(body)) // ✅ restore
    log.Println(string(body))
    c.Next()
}
```

## Do NOT assume `c.Request.Context()` is cancelled on timeout without checking

Gin's context is derived from `http.Request.Context()`. When you set a custom timeout middleware, the derived context is cancelled but `c.Request.Context()` may still be the original.

```go
// BAD: may not detect cancellation
func handler(c *gin.Context) {
    select {
    case <-c.Request.Context().Done(): // ❌ might not be cancelled yet
        return
    case <-time.After(5 * time.Second):
    }
}

// GOOD: use c.Request.Context() properly (Gin 1.8+ sets it correctly)
func handler(c *gin.Context) {
    ctx := c.Request.Context()
    result, err := doWork(ctx) // pass ctx to downstream
    if errors.Is(err, context.Canceled) || errors.Is(err, context.DeadlineExceeded) {
        return
    }
    c.JSON(200, result)
}
```

## Do NOT use `gin.Default()` in production without customizing recovery

`gin.Default()` uses `gin.Logger()` and `gin.Recovery()`. The default Recovery middleware prints stack traces to the response body, leaking internal code paths.

```go
// BAD: exposes stack traces to clients
r := gin.Default() // ❌ Recovery middleware leaks stack

// GOOD: custom recovery + logger
r := gin.New()
r.Use(gin.Logger())           // structured logging
r.Use(gin.CustomRecovery(func(c *gin.Context, err any) {
    c.AbortWithStatusJSON(500, gin.H{"error": "internal server error"})
}))
```

## Do NOT call `c.Next()` inside a condition that may skip it in middleware

Middleware MUST call `c.Next()` exactly once (unless aborted). Skipping `c.Next()` silently drops subsequent handlers.

```go
// BAD: skips c.Next() when token is missing — handler never runs
func ratelimit(c *gin.Context) {
    if ok := checkRate(c); ok {
        c.Next()
    }
    log.Println("rate check done") // runs either way
}

// GOOD: clear control flow
func ratelimit(c *gin.Context) {
    if !checkRate(c) {
        c.AbortWithStatusJSON(429, gin.H{"error": "too many requests"})
        return
    }
    c.Next()
}
```
