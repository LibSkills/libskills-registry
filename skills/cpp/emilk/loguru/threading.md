# Threading

### Thread safety guarantees
```cpp
// Loguru is thread-safe for logging operations
// Multiple threads can safely call LOG_F concurrently

#include <loguru.hpp>
#include <thread>
#include <vector>

void worker_thread(int id) {
    LOG_F(INFO, "Thread %d started", id);
    for (int i = 0; i < 100; ++i) {
        LOG_F(3, "Thread %d: iteration %d", id, i);
    }
    LOG_F(INFO, "Thread %d finished", id);
}

int main(int argc, char* argv[]) {
    loguru::init(argc, argv);
    loguru::add_file("threaded.log", loguru::Truncate, loguru::Verbosity_MAX);
    
    std::vector<std::thread> threads;
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back(worker_thread, i);
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    LOG_F(INFO, "All threads completed");
    return 0;
}
```

### Thread naming for better logs
```cpp
#include <loguru.hpp>
#include <thread>

void named_worker(const std::string& name) {
    loguru::set_thread_name(name.c_str());
    LOG_F(INFO, "This log shows thread name: %s", name.c_str());
}

int main(int argc, char* argv[]) {
    loguru::init(argc, argv);
    
    std::thread t1(named_worker, "NetworkThread");
    std::thread t2(named_worker, "WorkerThread");
    
    t1.join();
    t2.join();
    
    return 0;
}
```

### Concurrent access patterns
```cpp
// Safe: Multiple threads logging simultaneously
void safe_concurrent_logging() {
    std::thread t1([](){
        for (int i = 0; i < 1000; ++i) {
            LOG_F(INFO, "Thread 1: %d", i);
        }
    });
    
    std::thread t2([](){
        for (int i = 0; i < 1000; ++i) {
            LOG_F(INFO, "Thread 2: %d", i);
        }
    });
    
    t1.join();
    t2.join();
}

// UNSAFE: Modifying global state from multiple threads
void unsafe_global_modification() {
    std::thread t1([](){
        loguru::g_stderr_verbosity = 1; // UNSAFE - data race
    });
    
    std::thread t2([](){
        loguru::g_stderr_verbosity = 2; // UNSAFE - data race
    });
    
    t1.join();
    t2.join();
}
```

### Thread-local storage considerations
```cpp
// Loguru uses thread-local storage for scope indentation
// Each thread has its own indentation level

void scoped_thread_work() {
    LOG_SCOPE_F(INFO, "Thread scope");
    LOG_F(INFO, "Indented in this thread");
    
    std::thread t([](){
        LOG_F(INFO, "Not indented - different thread");
        LOG_SCOPE_F(INFO, "Inner scope");
        LOG_F(INFO, "Indented in inner scope");
    });
    t.join();
    
    LOG_F(INFO, "Still indented in original thread");
}
```