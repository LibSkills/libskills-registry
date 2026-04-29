# zap — Threading & Concurrency

## Thread Safety

- **`zap.Logger` is safe for concurrent use** — a single logger instance can be shared across all goroutines
- **`zap.SugaredLogger` is safe for concurrent use** — wraps Logger, inherits thread safety
- **`zap.AtomicLevel` is safe for concurrent use** — uses `atomic` operations
- **`zap.Logger.Sync()` is also safe for concurrent calls**

```go
// SAFE — share logger across goroutines
logger, _ := zap.NewProduction()
var wg sync.WaitGroup
for i := 0; i < 10; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        logger.Info("goroutine", zap.Int("id", id)) // ✅ safe
    }(i)
}
wg.Wait()
```

## Why Logger is Thread-Safe

zap internally uses a `WriteSyncer` (typically `os.File` or buffered writer) with locking. The encoder, while not thread-safe by itself, is used per-call and not shared between goroutines.

## One-Time Initialization

Use `sync.Once` for lazy logger initialization:

```go
var (
    once   sync.Once
    logger *zap.Logger
)

func GetLogger() *zap.Logger {
    once.Do(func() {
        var err error
        logger, err = zap.NewProduction()
        if err != nil {
            panic(err)
        }
    })
    return logger
}
```

## Fields in Concurrent Contexts

When using `logger.With(...)`, the returned logger shares the underlying core but has its own field list — safe for concurrent access.

```go
logger := zap.L().With(zap.String("request_id", reqID))
// Each goroutine can safely use its own logger instance
```
