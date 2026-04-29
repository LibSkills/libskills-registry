# Best Practices

### 1. Initialize with proper configuration
```cpp
#include <loguru.hpp>

int main(int argc, char* argv[]) {
    loguru::init(argc, argv);
    
    // Production configuration
    loguru::add_file("app.log", loguru::Append, loguru::Verbosity_MAX);
    loguru::add_file("errors.log", loguru::Truncate, loguru::Verbosity_WARNING);
    loguru::g_stderr_verbosity = loguru::Verbosity_WARNING;
    loguru::g_flush_interval_ms = 100; // Flush every 100ms
    
    LOG_F(INFO, "Application initialized");
    return 0;
}
```

### 2. Use scoped logging for function entry/exit
```cpp
void process_data(const std::vector<int>& data) {
    LOG_SCOPE_F(INFO, "process_data(size=%zu)", data.size());
    
    for (size_t i = 0; i < data.size(); ++i) {
        LOG_F(3, "Processing element %zu: %d", i, data[i]);
    }
    
    LOG_F(INFO, "Processing complete");
}
```

### 3. Implement error context for crash debugging
```cpp
void critical_operation(int value, const std::string& name) {
    loguru::set_error_context("value", value);
    loguru::set_error_context("name", name.c_str());
    
    CHECK_F(value > 0, "Invalid value");
    // On crash, error context is printed with stack trace
}
```

### 4. Use conditional logging for performance
```cpp
void expensive_operation(bool debug_mode) {
    LOG_IF_F(INFO, debug_mode, "Starting expensive operation");
    
    // Expensive computation
    int result = compute();
    
    LOG_IF_F(INFO, debug_mode, "Operation result: %d", result);
}
```

### 5. Configure fatal handler for graceful shutdown
```cpp
class Application {
public:
    void run() {
        loguru::set_fatal_handler([this](const loguru::Message& message) {
            save_state();
            notify_admin(message.message);
        });
        
        LOG_F(FATAL, "Critical failure");
    }
    
private:
    void save_state() { /* ... */ }
    void notify_admin(const std::string& msg) { /* ... */ }
};
```

### 6. Use verbosity levels consistently
```cpp
// Define application-specific verbosity constants
const int VERBOSITY_TRACE = 9;
const int VERBOSITY_DEBUG = 5;
const int VERBOSITY_INFO = 3;

void detailed_logging() {
    VLOG_F(VERBOSITY_TRACE, "Entering function");
    VLOG_F(VERBOSITY_DEBUG, "Intermediate state: %d", state);
    VLOG_F(VERBOSITY_INFO, "Operation completed");
}
```