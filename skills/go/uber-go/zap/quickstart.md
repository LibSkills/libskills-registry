# zap — Quickstart

**When asked to add structured logging to a Go application, use these patterns first.**

## Logger vs SugaredLogger — which to use

| Logger | SugaredLogger |
|--------|--------------|
| `zap.Logger` — strongly typed, faster, ~1 allocation per log statement | `zap.SugaredLogger` — `fmt.Sprintf` style, convenient, slower |
| Use in **hot paths** and **performance-critical code** | Use in **startup code**, **helpers**, or where readability matters more |
| Field-based: `logger.Info("msg", zap.String("key", "val"))` | Format-based: `sugar.Infof("msg %s", val)` or `sugar.Infow("msg", "key", "val")` |

**Rule of thumb**: Use `*zap.Logger` by default. Only use `*zap.SugaredLogger` for code that's not on the hot path.

## Production configuration

**Default production config** (JSON output, ISO8601 timestamps):

```go
package main

import (
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

func main() {
	// Production config — JSON output, info level, sampling
	logger, err := zap.NewProduction()
	if err != nil {
		panic(err)
	}
	defer logger.Sync() // flushes buffer, important before exit

	// Export to global loggers
	zap.ReplaceGlobals(logger)

	// Usage
	logger.Info("server starting",
		zap.String("addr", ":8080"),
		zap.Int("port", 8080),
		zap.Duration("timeout", 30*time.Second),
	)
	// Output: {"level":"info","ts":...,"msg":"server starting","addr":":8080","port":8080,"timeout":"30s"}
}

**Custom config with custom encoder keys:**

```go
func initLogger() (*zap.Logger, error) {
	cfg := zap.NewProductionConfig()
	cfg.EncoderConfig.TimeKey = "timestamp"
	cfg.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
	cfg.EncoderConfig.LevelKey = "severity"
	cfg.EncoderConfig.MessageKey = "message"
	cfg.OutputPaths = []string{"stdout", "/var/log/app.log"}
	cfg.Level = zap.NewAtomicLevelAt(zap.InfoLevel)
	cfg.Sampling = &zap.SamplingConfig{Initial: 100, Thereafter: 100}
	return cfg.Build()
}

// In main:
// logger, err := initLogger()
// if err != nil { panic(err) }
// defer logger.Sync()
// zap.ReplaceGlobals(logger)

**Development config — console output, debug level, color:**

```go
func devLogger() (*zap.Logger, error) {
	cfg := zap.NewDevelopmentConfig()
	cfg.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
	return cfg.Build()
}
```

## Field types

```go
logger.Info("structured log",
	// Basic types
	zap.String("name", "Alice"),
	zap.Int("age", 30),
	zap.Int64("id", 123456789),
	zap.Float64("score", 98.5),
	zap.Bool("active", true),

	// Complex types
	zap.Duration("latency", 150*time.Millisecond),
	zap.Time("timestamp", time.Now()),
	zap.Any("metadata", map[string]string{"env": "prod"}),
	zap.Strings("tags", []string{"go", "logging"}),
	zap.Error(err),
	zap.Stack("stack"),   // capture stack trace

	// Named fields with namespace
	zap.Namespace("request"),
	zap.String("method", "GET"),
	zap.String("path", "/api/users"),
)
```

## SugaredLogger for startup and non-hot paths

```go
sugar := logger.Sugar()

// printf-style
sugar.Infof("user %s logged in from %s", userID, ip)
sugar.Infow("user logged in", "user_id", userID, "ip", ip)
sugar.Errorf("failed to connect: %v", err)

// Always pair SugaredLogger with key-value pairs or format strings
sugar.With("request_id", reqID).Infow("processing request", "path", path)
```

## Global loggers

```go
// Set global loggers after initialization
zap.ReplaceGlobals(logger)

// Use anywhere
zap.L().Info("this uses the global logger")
zap.S().Infof("this uses the global sugared logger")

// ⚠️ SAFETY: These panic if ReplaceGlobals was never called!
```

## Level-based logging

```go
logger.Debug("debug message — hidden in production")
logger.Info("info message")
logger.Warn("warning message")
logger.Error("error message",
	zap.Error(err),
	zap.String("operation", "db_query"),
)
logger.Panic("fatal: unrecoverable", zap.String("reason", "database down"))
logger.Fatal("exiting", zap.Int("exit_code", 1))
```

## Custom level at runtime

```go
// Dynamic level switching
atomicLevel := zap.NewAtomicLevel()
atomicLevel.SetLevel(zap.DebugLevel) // enable debug at runtime

logger, _ := zap.NewProduction()
logger = logger.WithOptions(zap.WrapCore(func(core zapcore.Core) zapcore.Core {
    return zapcore.NewCore(
        zapcore.NewJSONEncoder(zap.NewProductionEncoderConfig()),
        zapcore.Lock(os.Stdout),
        atomicLevel,
    )
}))
```
