# zap — Best Practices

## Logger Creation

- **Initialize logger once** at application startup and store it in a package-level variable or pass via dependency injection
- **Use `zap.NewProduction()`** for production deployments
- **Use `zap.NewDevelopment()`** only for local development
- **Always handle the error** from `Build()` / `NewProduction()`
- **Always `defer logger.Sync()`** after creation

## Configuring Production Logger

```go
func NewProductionLogger() (*zap.Logger, error) {
    cfg := zap.NewProductionConfig()
    cfg.Level = zap.NewAtomicLevelAt(zap.InfoLevel)
    cfg.OutputPaths = []string{"stdout"}
    cfg.EncoderConfig.TimeKey = "timestamp"
    cfg.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
    cfg.Sampling = &zap.SamplingConfig{
        Initial:    100,
        Thereafter: 100,
    }
    return cfg.Build()
}
```

## Contextual Logging with Fields

```go
// Add persistent fields
logger := logger.With(
    zap.String("service", "user-api"),
    zap.String("version", version),
)

// Per-request fields
logger := logger.With(
    zap.String("request_id", requestID),
    zap.String("user_id", userID),
)
logger.Info("processing request")
```

## Logging Errors

```go
// Always use zap.Error for error fields
if err != nil {
    logger.Error("operation failed",
        zap.Error(err),
        zap.String("operation", "db_query"),
    )
}

// For expected errors, use Info or Warn
logger.Warn("retrying operation",
    zap.Error(err),
    zap.Int("attempt", attempt),
)
```

## Dynamic Level Switching

```go
atomicLevel := zap.NewAtomicLevel()
// Start at info, allow runtime switching
logger := zap.New(zapcore.NewCore(
    zapcore.NewJSONEncoder(zap.NewProductionEncoderConfig()),
    zapcore.Lock(os.Stdout),
    atomicLevel,
))

// Expose via HTTP for runtime changes
http.HandleFunc("/debug/log/level", atomicLevel.ServeHTTP)
```

## Logging Middleware Pattern

```go
func LoggingMiddleware(logger *zap.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()
            next.ServeHTTP(w, r)
            logger.Info("request",
                zap.String("method", r.Method),
                zap.String("path", r.URL.Path),
                zap.Int("status", w.(interface{ StatusCode() int }).StatusCode()),
                zap.Duration("duration", time.Since(start)),
            )
        })
    }
}
```
