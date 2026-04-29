# Safety

### 1. NEVER call LOG_F before loguru::init()
**BAD:**
```cpp
LOG_F(INFO, "Pre-init message"); // CRASH: uninitialized internal state
```

**GOOD:**
```cpp
loguru::init(argc, argv);
LOG_F(INFO, "Post-init message"); // Safe
```

### 2. NEVER use verbosity levels outside 0-9 range
**BAD:**
```cpp
VLOG_F(15, "Debug"); // Undefined behavior - out of range
VLOG_F(-5, "Error"); // Invalid negative verbosity
```

**GOOD:**
```cpp
VLOG_F(9, "Maximum debug"); // Valid range [0, 9]
VLOG_F(0, "Fatal"); // Minimum verbosity
```

### 3. NEVER pass null pointers to CHECK_F without checking
**BAD:**
```cpp
void process(int* ptr) {
    CHECK_F(ptr != nullptr); // OK, but then dereference without check
    *ptr = 42; // Still safe because CHECK aborts on null
}
```

**GOOD:**
```cpp
void process(int* ptr) {
    CHECK_F(ptr != nullptr, "Null pointer in process()");
    *ptr = 42; // Safe: guaranteed non-null after CHECK
}
```

### 4. NEVER modify loguru global state from multiple threads
**BAD:**
```cpp
// Thread 1
loguru::g_stderr_verbosity = 1;

// Thread 2 (concurrently)
loguru::g_stderr_verbosity = 2; // Data race!
```

**GOOD:**
```cpp
// Set global state before spawning threads
loguru::g_stderr_verbosity = 1;

// Now spawn threads that only use LOG_F
std::thread t1([](){ LOG_F(INFO, "Thread 1"); });
t1.join();
```

### 5. NEVER use LOG_S without defining LOGURU_WITH_STREAMS
**BAD:**
```cpp
#include <loguru.hpp>
LOG_S(INFO) << "Stream"; // Compilation error or undefined behavior
```

**GOOD:**
```cpp
#define LOGURU_WITH_STREAMS 1
#include <loguru.hpp>
LOG_S(INFO) << "Stream"; // Safe
```