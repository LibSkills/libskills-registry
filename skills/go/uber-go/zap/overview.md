# zap — Overview

**zap** is Uber's high-performance, structured logging library for Go. It provides two logging APIs — a strongly typed `Logger` and a `SugaredLogger` — with a focus on zero-allocation in hot paths.

## When to Use

- Any Go application that needs structured JSON logging
- Performance-sensitive services where allocation per log call matters
- Applications that need dynamic log levels, sampling, or custom encodings
- A lightweight alternative to `logrus` or `zerolog` when typing matters

## When NOT to Use

- Human-readable console logging for development (use `zap.NewDevelopmentConfig()` or consider `zerolog` for more colorful console output)
- Applications that need log aggregation without structured output (zap is designed for structured JSON)
- Extremely simple logging needs (Go's `log/slog` in Go 1.21+ may suffice)

## Key Design

- **Two APIs**: `zap.Logger` (fast, strongly typed) and `zap.SugaredLogger` (convenient, printf-style)
- **Field-based**: Logging uses typed fields (`zap.String`, `zap.Int`, `zap.Error`) for speed — no reflection, no allocations for primitives
- **Encoder abstraction**: JSON encoder for production, console encoder for development; custom encoders possible
- **Sampling**: Configurable sampling to reduce log volume in high-throughput systems
- **Levels**: Debug, Info, Warn, Error, DPanic, Panic, Fatal with atomic runtime switching
- **Hooks**: Per-level hooks for side effects (e.g., sending errors to Sentry)
- **Global loggers**: `zap.L()` and `zap.S()` return package-level loggers set via `zap.ReplaceGlobals()`
