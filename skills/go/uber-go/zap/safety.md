# zap — Safety

Red lines — conditions that must NEVER occur.

## NEVER call `zap.L()` or `zap.S()` before initialization

Calling any method on the global logger before `zap.ReplaceGlobals()` causes a nil pointer dereference panic.

```go
// NEVER — panic: runtime error: invalid memory address
func init() {
    zap.L().Info("initializing") // ❌ ReplaceGlobals not yet called
}

// ALWAYS: check and initialize globals first
func main() {
    logger, err := zap.NewProduction()
    if err != nil {
        panic(err)
    }
    zap.ReplaceGlobals(logger)

    // Now safe to use globals
    zap.L().Info("initialized")
}
```

## NEVER use `zap.NewDevelopmentConfig()` in production

Development config outputs to console (not JSON), uses debug level, and enables stack traces for warnings. It's verbose, unstructured, and produces more output than production systems can ingest.

```go
// NEVER — development config in production
logger, _ := zap.NewDevelopment() // ❌ console output, debug level, noisy stacks

// ALWAYS: production config for production
logger, _ := zap.NewProduction() // ✅ JSON, info level, sampled

// ALWAYS: custom production config with explicit settings
cfg := zap.NewProductionConfig()
cfg.Level = zap.NewAtomicLevelAt(zap.InfoLevel)
cfg.OutputPaths = []string{"stdout", "/var/log/app.log"}
logger, _ := cfg.Build()
```

## NEVER defer `logger.Sync()` after calling `logger.Fatal()`

`logger.Fatal()` calls `os.Exit(1)` internally. **Deferred functions do NOT run** after `os.Exit`.

```go
// NEVER — Sync never runs
logger, _ := zap.NewProduction()
defer logger.Sync() // ❌ will NOT run if Fatal is called
logger.Fatal("crashing")

// ALWAYS: call Sync before Fatal, or use Panic
logger, _ := zap.NewProduction()
logger.Sync()
logger.Fatal("crashing")

// ALWAYS: use Panic if deferred cleanup is required
logger, _ := zap.NewProduction()
defer logger.Sync()
defer db.Close()
logger.Panic("crashing with cleanup") // ✅ defer runs, then panics
```

## NEVER ignore the error return from `zap.NewProduction()` / `cfg.Build()`

Configuration errors (invalid output paths, bad encoder config) are returned as errors. Ignoring them silently creates a nil logger that panics on first use.

```go
// NEVER — nil logger on error
logger, _ := zap.NewProduction() // ❌ error silently discarded

// NEVER — ignoring cfg.Build error
cfg := zap.NewProductionConfig()
cfg.OutputPaths = []string{"/invalid/path/"} // won't open
logger, _ := cfg.Build()                      // ❌ error, logger is nil

// ALWAYS: handle the error
logger, err := zap.NewProduction()
if err != nil {
    panic(fmt.Sprintf("failed to create logger: %v", err))
}
```

## NEVER log sensitive data (passwords, tokens, PII) as structured fields

Structured logs go to files, stdout, and aggregation systems (Elasticsearch, Datadog, etc.). Sensitive data in logs creates compliance violations and security risks.

```go
// NEVER — logging sensitive data
logger.Info("user authenticated",
    zap.String("password", password),     // ❌ password in logs
    zap.String("token", authToken),       // ❌ token in logs
    zap.String("ssn", user.SSN),          // ❌ PII in logs
)

// ALWAYS: redact, mask, or exclude
logger.Info("user authenticated",
    zap.String("user_id", user.ID),
    zap.Bool("auth_success", true),
    zap.String("ip", user.IP),            // OK for many cases, check your policy
)
```

## NEVER use `zap.Any` for large blob data on hot paths

`zap.Any` serializes via reflection and allocates. On hot paths it becomes a performance bottleneck.

```go
// NEVER — large struct serialized every log call
logger.Info("request",
    zap.Any("body", requestBody),     // ❌ huge allocation per request
)

// ALWAYS: log selective fields
logger.Info("request",
    zap.Int("body_size", len(requestBody)),
    zap.String("method", requestBody.Method),
    zap.Int("item_count", len(requestBody.Items)),
)
```
