# zap — Performance

## Zero-Allocation Design

zap's `Logger` API is designed to minimize allocations:

- **Typed fields** (`zap.String`, `zap.Int`, `zap.Error`) — no reflection, no boxing
- **Pre-allocated field arrays** — fields are stack-allocated in most cases
- **No varargs** — Logger methods take a fixed message followed by variadic `zap.Field`, but fields are created inline

## Performance Comparison (approximate)

| Operation | Logger (typed) | SugaredLogger | log.Printf | logrus |
|-----------|---------------|---------------|------------|--------|
| Simple log (no fields) | ~0 allocs | ~1 alloc | ~0 allocs | ~2 allocs |
| Log with 3 fields | ~0 allocs | ~3-5 allocs | N/A | ~5-8 allocs |
| Log with format string | ~0 allocs | ~1 alloc + formatting | ~1 alloc | ~2-3 allocs |

## When to Use Each API

```go
// HOT PATH — use Logger with typed fields
func (s *Service) HandleRequest(ctx context.Context, req *Request) {
    s.logger.Info("request",
        zap.String("method", req.Method),
        zap.String("path", req.Path),
        zap.Int64("user_id", req.UserID),
    )
}

// WARM PATH — SugaredLogger is fine for moderate use
func (s *Service) ProcessItem(item Item) {
    s.logger.Sugar().Infow("processing",
        "item_id", item.ID,
        "type", item.Type,
    )
}

// COLD PATH — SugaredLogger with format strings
func (s *Service) LogConfig() {
    s.logger.Sugar().Infof("config: port=%d, debug=%v", cfg.Port, cfg.Debug)
}
```

## Sampling

Prevent log storms in high-throughput systems:

```go
cfg.Sampling = &zap.SamplingConfig{
    Initial:    100,    // log first 100 messages per second
    Thereafter: 100,    // then log every 100th message
}
```

## Encoder Selection

- **JSON encoder** (`zapcore.NewJSONEncoder`) — fastest, best for production
- **Console encoder** (`zapcore.NewConsoleEncoder`) — slower due to color+formatting, dev only

## Field Allocation Note

`zap.Any` is the only field type that always allocates (it uses reflection). Avoid it in hot paths.
