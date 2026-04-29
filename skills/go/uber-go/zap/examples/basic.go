package main

import (
	"errors"
	"net/http"
	"time"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

func main() {
	// --- Production Logger ---
	logger, err := zap.NewProduction()
	if err != nil {
		panic(err)
	}
	defer logger.Sync() // flush before exit

	// Set as global logger
	zap.ReplaceGlobals(logger)

	// --- Basic logging ---
	logger.Info("service starting",
		zap.String("service", "example-api"),
		zap.String("version", "1.0.0"),
	)

	// --- Error logging ---
	err = errors.New("connection refused")
	logger.Error("failed to connect to database",
		zap.Error(err),
		zap.String("host", "localhost"),
		zap.Int("port", 5432),
		zap.Int("retry_count", 3),
	)

	// --- With fields (contextual) ---
	reqLogger := logger.With(
		zap.String("request_id", "req-123"),
		zap.String("user_id", "user-456"),
	)

	reqLogger.Info("processing request",
		zap.String("method", "GET"),
		zap.String("path", "/api/users"),
		zap.Duration("latency", 45*time.Millisecond),
	)

	// --- SugaredLogger ---
	sugar := logger.Sugar()

	// printf-style logging (cold path only)
	sugar.Infof("server listening on port %d", 8080)

	// key-value logging
	sugar.Infow("user action",
		"action", "login",
		"user", "alice",
		"ip", "192.168.1.1",
	)

	// --- Dynamic level ---
	atomicLevel := zap.NewAtomicLevel()
	atomicLevel.SetLevel(zap.DebugLevel) // enable debug at runtime

	dynamicLogger := zap.New(zapcore.NewCore(
		zapcore.NewJSONEncoder(zap.NewProductionEncoderConfig()),
		zapcore.Lock(logger.Core().(zapcore.CoreWithIO).IO()),
		atomicLevel,
	))
	_ = dynamicLogger

	// --- HTTP middleware example ---
	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"ok"}`))
	})

	handler := zapMiddleware(logger)(mux)

	srv := &http.Server{
		Addr:    ":8080",
		Handler: handler,
	}

	logger.Info("starting HTTP server", zap.String("addr", srv.Addr))
	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		logger.Fatal("server error", zap.Error(err))
	}
}

// --- Middleware ---

func zapMiddleware(logger *zap.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()

			// Wrap ResponseWriter to capture status code
			lrw := &loggingResponseWriter{ResponseWriter: w, statusCode: http.StatusOK}
			next.ServeHTTP(lrw, r)

			logger.Info("http request",
				zap.String("method", r.Method),
				zap.String("path", r.URL.Path),
				zap.String("remote", r.RemoteAddr),
				zap.Int("status", lrw.statusCode),
				zap.Duration("duration", time.Since(start)),
				zap.String("user_agent", r.UserAgent()),
			)
		})
	}
}

type loggingResponseWriter struct {
	http.ResponseWriter
	statusCode int
}

func (lrw *loggingResponseWriter) WriteHeader(code int) {
	lrw.statusCode = code
	lrw.ResponseWriter.WriteHeader(code)
}
