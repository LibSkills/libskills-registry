# Performance

### Performance characteristics
```cpp
// Loguru is designed for minimal overhead
// Typical performance: 3-8 microseconds per log call

#include <loguru.hpp>
#include <chrono>

void benchmark_logging() {
    loguru::init(0, nullptr);
    loguru::add_file("bench.log", loguru::Truncate, loguru::Verbosity_MAX);
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < 10000; ++i) {
        LOG_F(INFO, "Benchmark iteration %d", i);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    LOG_F(INFO, "Average time per log: %.2f us", duration.count() / 10000.0);
}
```

### Allocation patterns
```cpp
// Loguru minimizes allocations during logging
// Pre-allocated buffers are used for formatting

void allocation_safe_logging() {
    // No dynamic allocation for simple messages
    LOG_F(INFO, "Simple message"); // Uses stack buffer
    
    // Long messages may allocate
    std::string long_msg(10000, 'x');
    LOG_F(INFO, "%s", long_msg.c_str()); // May allocate for large strings
}
```

### Optimization tips
```cpp
// 1. Use flush interval for better performance
void configure_performance() {
    loguru::g_flush_interval_ms = 100; // Batch flushes every 100ms
    // Without this, each log call flushes immediately (slower)
}

// 2. Use conditional logging to avoid expensive formatting
void expensive_formatting() {
    int x = 42, y = 100;
    
    // BAD: Always evaluates arguments
    LOG_F(9, "x=%d, y=%d, result=%d", x, y, expensive_computation(x, y));
    
    // GOOD: Only evaluates when verbosity is high enough
    if (loguru::g_stderr_verbosity >= 9) {
        LOG_F(9, "x=%d, y=%d, result=%d", x, y, expensive_computation(x, y));
    }
}

// 3. Use VLOG_F for dynamic verbosity control
void dynamic_verbosity(int level) {
    VLOG_F(level, "Dynamic message"); // Same performance as LOG_F
}
```

### Compile-time optimization
```cpp
// Loguru's header has no includes for fast compilation
// This gives ~10% faster compilation compared to GLOG

// BAD: Including loguru.hpp with streams enabled everywhere
#define LOGURU_WITH_STREAMS 1
#include <loguru.hpp> // Now includes <sstream> - slower compilation

// GOOD: Only enable streams where needed
// In most files:
#include <loguru.hpp> // Fast - no includes

// In files that need streams:
#define LOGURU_WITH_STREAMS 1
#include <loguru.hpp> // Slower, but only in this file
```