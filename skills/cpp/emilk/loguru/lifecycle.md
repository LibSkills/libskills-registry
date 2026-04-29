# Lifecycle

### Construction and initialization
```cpp
#include <loguru.hpp>

// Loguru must be initialized before use
int main(int argc, char* argv[]) {
    // init() parses command line for -v verbosity flag
    loguru::init(argc, argv);
    
    // Configure logging destinations
    loguru::add_file("app.log", loguru::Truncate, loguru::Verbosity_MAX);
    
    // Set global options
    loguru::g_stderr_verbosity = loguru::Verbosity_INFO;
    loguru::g_colorlogtostderr = true;
    loguru::g_flush_interval_ms = 0; // Immediate flush
    
    LOG_F(INFO, "Loguru initialized");
    return 0;
}
```

### Resource management
```cpp
// Loguru manages its own resources internally
// No explicit cleanup needed - resources freed on program exit

void configure_logging() {
    // add_file returns bool indicating success
    bool success = loguru::add_file("log.txt", loguru::Append, loguru::Verbosity_MAX);
    if (!success) {
        LOG_F(ERROR, "Failed to add log file");
    }
    
    // Multiple files can be added
    loguru::add_file("debug.log", loguru::Truncate, loguru::Verbosity_MAX);
    loguru::add_file("errors.log", loguru::Truncate, loguru::Verbosity_WARNING);
}
```

### No move semantics needed
```cpp
// Loguru is a singleton-style library - no objects to move
// All operations are through static functions

// BAD: Trying to move Loguru state
// loguru::init(argc, argv); // Can't move this

// GOOD: Just call functions directly
loguru::init(argc, argv);
loguru::add_file("log.txt", loguru::Truncate, loguru::Verbosity_MAX);
```

### Shutdown behavior
```cpp
// Loguru flushes all pending output on program exit
// No explicit shutdown needed

void cleanup() {
    LOG_F(INFO, "Shutting down");
    // Loguru automatically flushes and closes files
    // on normal program termination
}

int main(int argc, char* argv[]) {
    loguru::init(argc, argv);
    loguru::add_file("log.txt", loguru::Truncate, loguru::Verbosity_MAX);
    
    cleanup();
    return 0; // Loguru flushes and cleans up here
}
```