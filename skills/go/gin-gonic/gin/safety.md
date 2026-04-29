# Gin — Safety

Red lines — conditions that must NEVER occur.

## NEVER access `*gin.Context` in a goroutine without extracting values first

Gin reuses contexts from a `sync.Pool`. After the handler returns, the context is recycled. Concurrent reads in a goroutine cause data races.

```go
// NEVER
func handler(c *gin.Context) {
    go func() {
        c.JSON(200, gin.H{"user": c.GetString("user")}) // ❌ races
    }()
}

// ALWAYS: extract before goroutine
func handler(c *gin.Context) {
    user := c.GetString("user")
    go func() {
        // use 'user', not c
    }()
}
```

## NEVER write to the response after `c.Abort()`

`Abort()` marks the context as aborted but does not panic or stop execution. Writing after abort produces a second `WriteHeader` call (logged but confusing) and may silently drop data.

```go
// NEVER
func auth(c *gin.Context) {
    if !valid(c) {
        c.AbortWithStatusJSON(401, gin.H{"error": "unauthorized"})
        c.JSON(200, gin.H{"data": "sensitive"}) // ❌ double write
    }
}

// ALWAYS: return after abort
func auth(c *gin.Context) {
    if !valid(c) {
        c.AbortWithStatusJSON(401, gin.H{"error": "unauthorized"})
        return
    }
    c.Next()
}
```

## NEVER use `gin.Default()` Recovery middleware in production

The default `gin.Recovery()` writes full stack traces to the HTTP response body. This leaks internal source paths, function signatures, and potential secrets.

```go
// NEVER — leaks stack trace to client
r := gin.Default() // Recovery → returns stack on panic

// ALWAYS — controlled error response
r := gin.New()
r.Use(gin.CustomRecovery(func(c *gin.Context, err any) {
    c.AbortWithStatusJSON(500, gin.H{"error": "internal error"})
}))
```

## NEVER bind request into a global or shared struct without synchronization

Gin's binding functions modify the target struct in-place. Concurrent requests binding to the same struct cause data races.

```go
// NEVER
var user User // shared across requests
func handler(c *gin.Context) {
    if err := c.ShouldBindJSON(&user); err != nil { // ❌ data race
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
}

// ALWAYS: allocate fresh per request
func handler(c *gin.Context) {
    var user User
    if err := c.ShouldBindJSON(&user); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
}
```

## NEVER ignore the error return from `c.ShouldBind*`

Binding failure leaves the target struct partially populated. Continuing with unvalidated data creates security vulnerabilities.

```go
// NEVER
var input CreateUserReq
c.ShouldBindJSON(&input)                    // ❌ error ignored
if input.Email == "" {
    // validation may already be wrong — input may be partially bound
}

// ALWAYS
var input CreateUserReq
if err := c.ShouldBindJSON(&input); err != nil {
    c.JSON(400, gin.H{"error": err.Error()})
    return
}
```

## NEVER use a raw `http.Handler` or `http.HandlerFunc` as gin middleware

Wrapping raw `http.Handler` via `gin.WrapH()` discards Gin's context, breaking middleware chain, `c.Set()`/`c.Get()`, and path parameters.

```go
// NEVER
r.Use(gin.WrapH(myHTTPHandler)) // ❌ loses gin.Context entirely

// ALWAYS: implement as gin.HandlerFunc
r.Use(func(c *gin.Context) {
    myHandler(c.Writer, c.Request) // pass underlying writer/request
    // but c.Next() won't work correctly
})

// ALWAYS PREFERRED: pure gin middleware
r.Use(func(c *gin.Context) {
    // do gin-native work
    c.Next()
})
```
