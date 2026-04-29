# Gin — Best Practices

## Recommended Project Structure

```
cmd/server/main.go      # entry point: init router, start server
internal/handler/       # HTTP handlers — thin, call services
internal/middleware/    # custom middleware
internal/service/       # business logic
internal/model/         # data types, DTOs
internal/router/        # route registration
```

## Always Return After Abort

Every `c.Abort*()` call must be immediately followed by `return`. Gin does not throw or panic on abort.

```go
func adminOnly(c *gin.Context) {
    if !isAdmin(c) {
        c.AbortWithStatusJSON(403, gin.H{"error": "forbidden"})
        return // mandatory
    }
    c.Next()
}
```

## Use `c.Set()` / `c.Get()` For Request-Scoped Values

Pass values through the middleware chain instead of using global state or context.Background().

```go
func authMiddleware(c *gin.Context) {
    user := parseToken(c)
    c.Set("user", user) // request-scoped
    c.Next()
}

func handler(c *gin.Context) {
    user, _ := c.Get("user") // retrieve downstream
    c.JSON(200, gin.H{"user": user})
}
```

## Graceful Shutdown In main()

```go
func main() {
    r := gin.New()
    r.Use(gin.Logger(), gin.Recovery())
    r.GET("/health", func(c *gin.Context) {
        c.JSON(200, gin.H{"status": "ok"})
    })

    srv := &http.Server{
        Addr:    ":8080",
        Handler: r,
    }

    go func() {
        if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
            log.Fatalf("listen: %s\n", err)
        }
    }()

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    if err := srv.Shutdown(ctx); err != nil {
        log.Fatalf("shutdown: %s\n", err)
    }
}
```

## Use Struct Binding With Custom Validation

```go
type CreateUserReq struct {
    Email  string `json:"email"  binding:"required,email"`
    Age    int    `json:"age"    binding:"gte=0,lte=150"`
    Name   string `json:"name"   binding:"required,min=2,max=100"`
}

func createUser(c *gin.Context) {
    var req CreateUserReq
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    // req is validated — use it
    c.JSON(201, gin.H{"email": req.Email})
}
```

## Serve Static Files Correctly

```go
// Single file
r.StaticFile("/favicon.ico", "./assets/favicon.ico")

// Directory (strips /static prefix)
r.Static("/static", "./public")

// FileSystem for embedded files
// r.StaticFS("/static", http.FS(embedFS))
```
