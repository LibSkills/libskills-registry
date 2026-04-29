# zap — Lifecycle

## Initialization

1. Create logger with `zap.NewProduction()`, `zap.NewDevelopment()`, or `cfg.Build()`
2. Configure output paths, level, encoding, and sampling
3. Optionally call `zap.ReplaceGlobals(logger)` to enable `zap.L()` / `zap.S()`
4. Optionally call `zap.RedirectStdLog(logger)` to redirect `log.Print` to zap
5. `defer logger.Sync()` to flush buffered output on shutdown

## Logger Lifecycle in an Application

```go
func main() {
    // 1. Create logger
    logger, err := zap.NewProduction()
    if err != nil {
        log.Fatalf("failed to create logger: %v", err)
    }
    defer logger.Sync()

    // 2. Set as global
    zap.ReplaceGlobals(logger)

    // 3. Redirect standard library logger
    zap.RedirectStdLog(logger)

    // 4. Use throughout application
    srv := NewServer(logger)
    srv.Start()

    // 5. Sync on shutdown (via defer)
}
```

## Shutdown

- Call `logger.Sync()` before `os.Exit` or `log.Fatal`
- `Sync()` flushes buffered log entries to the underlying writer
- Without `Sync()`, the last few log lines may be lost on abnormal exit

## Runtime Reconfiguration

- Use `zap.AtomicLevel` for dynamic level changes without restart
- Change output paths by rebuilding the logger with new config
- Add/remove fields by using `logger.With(...)` to create a new logger instance (cheap, fields are shared internally)
