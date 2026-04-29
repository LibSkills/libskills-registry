# Quickstart

```cpp
#include <loguru.hpp>

// 1. Basic initialization with command line args
int main(int argc, char* argv[]) {
    loguru::init(argc, argv);
    
    // 2. Simple logging at different verbosity levels
    LOG_F(INFO, "Application started");
    LOG_F(WARNING, "Disk space is low: %.1f GB remaining", 2.3);
    LOG_F(ERROR, "Failed to connect to server");
    LOG_F(FATAL, "Critical system failure");
    
    // 3. Logging with dynamic verbosity
    int verbosity = 3;
    VLOG_F(verbosity, "Detailed debug info: x=%d, y=%d", 10, 20);
    
    // 4. Conditional logging
    bool is_error = true;
    LOG_IF_F(ERROR, is_error, "Error condition detected");
    
    // 5. Assertions with CHECK macros
    int* ptr = new int(42);
    CHECK_F(ptr != nullptr, "Pointer should not be null");
    CHECK_EQ_F(42, *ptr, "Value mismatch: expected %d", 42);
    CHECK_GT_F(*ptr, 0, "Value must be positive");
    
    // 6. File output configuration
    loguru::add_file("everything.log", loguru::Append, loguru::Verbosity_MAX);
    loguru::add_file("errors.log", loguru::Truncate, loguru::Verbosity_WARNING);
    
    // 7. Scoped indentation
    LOG_SCOPE_F(INFO, "Processing user data");
    LOG_F(INFO, "Inside scope - indented");
    LOG_F(INFO, "Still indented");
    // Scope ends, indentation resets
    
    // 8. Stream-style logging (requires #define LOGURU_WITH_STREAMS 1)
    #ifdef LOGURU_WITH_STREAMS
    LOG_S(INFO) << "Stream-style logging: " << 42 << " items processed";
    #endif
    
    return 0;
}
```