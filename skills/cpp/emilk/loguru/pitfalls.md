# Pitfalls

### 1. Forgetting to initialize Loguru
**BAD:**
```cpp
#include <loguru.hpp>

int main() {
    LOG_F(INFO, "Starting"); // Undefined behavior - not initialized
    loguru::add_file("log.txt", loguru::Truncate, loguru::Verbosity_MAX);
    return 0;
}
```

**GOOD:**
```cpp
#include <loguru.hpp>

int main(int argc, char* argv[]) {
    loguru::init(argc, argv); // Must call before any logging
    loguru::add_file("log.txt", loguru::Truncate, loguru::Verbosity_MAX);
    LOG_F(INFO, "Starting");
    return 0;
}
```

### 2. Using incorrect verbosity levels
**BAD:**
```cpp
LOG_F(10, "Debug message"); // Verbosity 10 is out of range (0-9)
LOG_F(-1, "Critical error"); // Negative verbosity is invalid
```

**GOOD:**
```cpp
LOG_F(9, "Maximum debug verbosity"); // Valid range 0-9
LOG_F(INFO, "Standard info message"); // Use named constants
LOG_F(FATAL, "Fatal error"); // Verbosity 0
```

### 3. Mixing printf and stream styles without proper defines
**BAD:**
```cpp
#include <loguru.hpp>
LOG_S(INFO) << "Stream message"; // Error: LOGURU_WITH_STREAMS not defined
```

**GOOD:**
```cpp
#define LOGURU_WITH_STREAMS 1
#include <loguru.hpp>
LOG_S(INFO) << "Stream message"; // Works correctly
```

### 4. Not checking file open success
**BAD:**
```cpp
loguru::add_file("/invalid/path/log.txt", loguru::Truncate, loguru::Verbosity_MAX);
// No error checking - file might not be created
```

**GOOD:**
```cpp
if (!loguru::add_file("log.txt", loguru::Truncate, loguru::Verbosity_MAX)) {
    LOG_F(ERROR, "Failed to create log file");
}
```

### 5. Using CHECK macros with side effects
**BAD:**
```cpp
int counter = 0;
CHECK_F(increment(counter) > 0, "Counter should be positive"); // Side effect in CHECK
```

**GOOD:**
```cpp
int counter = 0;
int result = increment(counter);
CHECK_F(result > 0, "Counter should be positive, got %d", result);
```

### 6. Ignoring thread safety for file operations
**BAD:**
```cpp
// Thread 1
loguru::add_file("log1.txt", loguru::Truncate, loguru::Verbosity_MAX);

// Thread 2 (concurrently)
loguru::add_file("log2.txt", loguru::Truncate, loguru::Verbosity_MAX);
// Race condition on internal state
```

**GOOD:**
```cpp
// Initialize all files before spawning threads
loguru::add_file("log1.txt", loguru::Truncate, loguru::Verbosity_MAX);
loguru::add_file("log2.txt", loguru::Truncate, loguru::Verbosity_MAX);

// Now spawn threads that only use LOG_F macros
std::thread t1([](){ LOG_F(INFO, "Thread 1"); });
std::thread t2([](){ LOG_F(INFO, "Thread 2"); });
t1.join();
t2.join();
```

### 7. Using DCHECK in release builds expecting checks
**BAD:**
```cpp
void process(int* ptr) {
    DCHECK_F(ptr != nullptr, "Pointer must be valid"); // Only checked in debug
    *ptr = 42; // Crash in release if ptr is null
}
```

**GOOD:**
```cpp
void process(int* ptr) {
    CHECK_F(ptr != nullptr, "Pointer must be valid"); // Checked in all builds
    *ptr = 42;
}
```

### 8. Not handling fatal errors gracefully
**BAD:**
```cpp
LOG_F(FATAL, "Critical error"); // Aborts program immediately
// Cleanup code never runs
```

**GOOD:**
```cpp
loguru::set_fatal_handler([](const loguru::Message& message){
    // Perform cleanup before abort
    cleanup_resources();
    std::cerr << "Fatal: " << message.message << std::endl;
});

LOG_F(FATAL, "Critical error"); // Handler runs before abort
```