# zap — Pitfalls

Common mistakes that cause panics, silent log loss, or performance degradation.

## Using global loggers before initialization

Calling `zap.L()` or `zap.S()` without first calling `zap.ReplaceGlobals()` causes a panic.

```go
// BAD: panic — global logger not initialized
func init() {
    zap.L().Info("initializing") // ❌ panic: global logger not set
}

// GOOD: initialize globals at the start of main()
func main() {
    logger, _ := zap.NewProduction()
    zap.ReplaceGlobals(logger)
    defer logger.Sync()
    zap.L().Info("initializing") // ✅ OK
}

// GOOD: initialize in init() if you must
var logger *zap.Logger

func init() {
    var err error
    logger, err = zap.NewProduction()
    if err != nil {
        panic(err)
    }
}
```

## Using SugaredLogger on performance-critical paths

SugaredLogger uses reflection and heap-allocates variadic args, making it unsuitable for hot paths.

```go
// BAD: SugaredLogger in hot path (hundreds of calls per request)
func (s *Service) Process(items []Item) {
    for _, item := range items {
        s.logger.Sugar().Infow("processing item",
            "id", item.ID,     // ❌ allocates per call
            "type", item.Type,
        )
    }
}

// GOOD: use Logger in hot paths
func (s *Service) Process(items []Item) {
    for _, item := range items {
        s.logger.Info("processing item",
            zap.String("id", item.ID),    // ✅ zero alloc
            zap.String("type", item.Type),
        )
    }
}

// OK: use SugaredLogger for startup, config, and error reporting
func (s *Service) Start() {
    s.logger.Sugar().Infof("service starting on port %d", s.cfg.Port)
}
```

## Format strings with SugaredLogger causing panics

Mismatched format verbs cause panics in `SugaredLogger.Infof` / `Errorf`.

```go
// BAD: wrong format verb — panic
id := 42
sugar.Infof("user id is %s", id) // ❌ panic: %s wants string, got int

// GOOD: use correct verb
sugar.Infof("user id is %d", id) // ✅
sugar.Infow("user", "id", id)    // ✅ key-value, no format string

// BETTER: use Logger
logger.Info("user", zap.Int("id", id)) // ✅ typed, no format string
```

## Debug logs enabled in production

Debug logs create overhead even if not observed — zap still evaluates structured fields.

```go
// BAD: debug logging in production — overhead even at Info level
logger.Debug("query result",
    zap.Any("rows", largeResultSet),   // ❌ evaluated even if Debug is off
)

// GOOD: check level first for expensive operations
if logger.Core().Enabled(zap.DebugLevel) {
    logger.Debug("query result",
        zap.Any("rows", largeResultSet),
    )
}

// GOOD: use zap.Field wrappers that lazily evaluate
// (zap.Any where the value is not huge is fine without the check)
```

## Forgetting `logger.Sync()` on exit

zap uses buffered writers. If the program exits without `Sync()`, the last log lines may be lost.

```go
// BAD: exiting without sync — last log lines lost on crash
func main() {
    logger, _ := zap.NewProduction()
    logger.Info("about to crash")
    os.Exit(1) // ❌ logs may not be flushed
}

// GOOD: defer Sync() on initialization
func main() {
    logger, _ := zap.NewProduction()
    defer logger.Sync() // ✅ flushes no matter what
    logger.Info("about to crash")
    os.Exit(1) // sync runs before exit
}
```

## Not passing the same logger through context

Creating new loggers per function loses fields and makes tracing hard.

```go
// BAD: lost context fields
func handleRequest(ctx context.Context) {
    logger := zap.L() // ❌ loses request_id and user_id
    logger.Info("handling request")
}

// GOOD: pass logger through context
type contextKey struct{}

func WithLogger(ctx context.Context, logger *zap.Logger) context.Context {
    return context.WithValue(ctx, contextKey{}, logger)
}

func LoggerFromContext(ctx context.Context) *zap.Logger {
    if l, ok := ctx.Value(contextKey{}).(*zap.Logger); ok {
        return l
    }
    return zap.L()
}

// Usage
func handleRequest(ctx context.Context) {
    logger := LoggerFromContext(ctx).
        With(zap.String("handler", "handleRequest"))
    logger.Info("handling request")
}
```

## Confusing `Fatal` and `Panic`

`logger.Fatal(msg)` calls `os.Exit(1)` after logging — **deferred functions don't run**. `logger.Panic(msg)` panics after logging — deferred functions DO run.

```go
// BAD: deferred Sync() won't run after Fatal
func main() {
    logger, _ := zap.NewProduction()
    defer logger.Sync() // ❌ never runs after Fatal
    if err != nil {
        logger.Fatal("failed to start") // calls os.Exit(1)
    }
}

// GOOD: call Sync before Fatal, or use Panic instead
if err != nil {
    logger.Sync()
    logger.Fatal("failed to start")
}

// GOOD: use Panic if deferred cleanup is needed
defer logger.Sync()
defer db.Close()
if err != nil {
    logger.Panic("failed to start") // ✅ defer runs, then panics
}
```
