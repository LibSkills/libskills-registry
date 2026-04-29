# Performance


```cpp
// Performance characteristic: Stack trace capture is expensive
#include "backward.hpp"
#include <chrono>
#include <iostream>

void benchmark_capture() {
    auto start = std::chrono::high_resolution_clock::now();
    
    backward::StackTrace st;
    st.load_here(32);  // ~100-500 microseconds
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    std::cout << "Stack capture took: " << duration << " us\n";
    
    // Printing is even more expensive (can be 10-100x slower)
    start = std::chrono::high_resolution_clock::now();
    backward::Printer().print(st);  // ~1-50 milliseconds
    end = std::chrono::high_resolution_clock::now();
    duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    std::cout << "Stack printing took: " << duration << " us\n";
}
```

```cpp
// Optimization: Limit stack depth and avoid printing in hot paths
#include "backward.hpp"
#include <atomic>

class OptimizedTracer {
    std::atomic<size_t> trace_count_{0};
    static constexpr size_t MAX_TRACES_PER_SECOND = 100;
    
public:
    void trace_if_needed() {
        // Rate limiting to avoid performance impact
        if (trace_count_.fetch_add(1) >= MAX_TRACES_PER_SECOND) {
            return;  // Skip trace to maintain performance
        }
        
        backward::StackTrace st;
        st.load_here(16);  // Limit depth to 16 frames for speed
        
        // Only resolve if we have time
        backward::TraceResolver tr;
        tr.load_stacktrace(st);
        
        // Print to string stream instead of stdout
        std::stringstream ss;
        backward::Printer p;
        p.print(st, ss);
        
        // Log the trace string
        log_trace(ss.str());
    }
    
    void log_trace(const std::string& trace) {
        // Implementation depends on logging system
    }
};
```

```cpp
// Allocation patterns: Avoid repeated allocations
#include "backward.hpp"
#include <vector>

class TracePool {
    std::vector<backward::StackTrace> pool_;
    size_t current_{0};
public:
    TracePool(size_t size) : pool_(size) {}
    
    backward::StackTrace& acquire() {
        auto& st = pool_[current_ % pool_.size()];
        st.load_here(32);
        current_++;
        return st;
    }
    
    void print_all() {
        backward::Printer p;
        for (auto& st : pool_) {
            p.print(st);
        }
    }
};

int main() {
    TracePool pool(10);  // Pre-allocate 10 trace objects
    
    for (int i = 0; i < 100; ++i) {
        auto& st = pool.acquire();  // Reuses existing objects
        // Process trace...
    }
    
    return 0;
}
```

```cpp
// Performance tip: Use string streams for deferred printing
#include "backward.hpp"
#include <sstream>
#include <queue>
#include <thread>

class AsyncTraceLogger {
    std::queue<std::string> trace_queue_;
    std::mutex mutex_;
    
public:
    void capture_trace() {
        backward::StackTrace st;
        st.load_here(32);
        
        // Print to string stream (faster than stdout)
        std::stringstream ss;
        backward::Printer p;
        p.print(st, ss);
        
        // Queue for later processing
        std::lock_guard<std::mutex> lock(mutex_);
        trace_queue_.push(ss.str());
    }
    
    void flush_traces() {
        std::lock_guard<std::mutex> lock(mutex_);
        while (!trace_queue_.empty()) {
            std::cout << trace_queue_.front();
            trace_queue_.pop();
        }
    }
};
```