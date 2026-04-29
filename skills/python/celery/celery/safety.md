# Safety

**Red Line 1: NEVER use uninitialized Celery app**

```cpp
// BAD: Using app before initialization
celery::Celery app; // Default constructed
auto result = app.send_task(celery::Task("task")); // Undefined behavior
```

```cpp
// GOOD: Always initialize with valid broker URL
celery::Celery app("redis://localhost:6379/0");
// Or check initialization
if (!app.is_initialized()) {
    throw std::runtime_error("Celery not initialized");
}
```

**Red Line 2: NEVER ignore task exceptions silently**

```cpp
// BAD: Swallowing exceptions
auto result = app.send_task(celery::Task("risky_task"));
try {
    std::string output = result.get();
} catch (...) {
    // Silently ignoring - data loss possible
}
```

```cpp
// GOOD: Always handle task exceptions
auto result = app.send_task(celery::Task("risky_task"));
try {
    std::string output = result.get();
} catch (const celery::TaskException& e) {
    log_error("Task failed: " + std::string(e.what()));
    // Implement proper error recovery
    throw; // Or re-raise if can't handle
}
```

**Red Line 3: NEVER share Celery app across threads without synchronization**

```cpp
// BAD: Unsafe concurrent access
celery::Celery app("redis://localhost:6379/0");
std::thread t1([&]() { app.send_task(celery::Task("task1")); });
std::thread t2([&]() { app.send_task(celery::Task("task2")); });
// Race condition on internal state
```

```cpp
// GOOD: Thread-safe usage
celery::Celery app("redis://localhost:6379/0");
std::mutex mtx;
std::thread t1([&]() { 
    std::lock_guard<std::mutex> lock(mtx);
    app.send_task(celery::Task("task1")); 
});
std::thread t2([&]() { 
    std::lock_guard<std::mutex> lock(mtx);
    app.send_task(celery::Task("task2")); 
});
```

**Red Line 4: NEVER use expired or revoked task results**

```cpp
// BAD: Using stale results
auto result = app.send_task(celery::Task("old_task"));
std::this_thread::sleep_for(std::chrono::hours(24));
std::string output = result.get(); // Result may be expired
```

```cpp
// GOOD: Check result validity
auto result = app.send_task(celery::Task("task"));
if (result.is_expired()) {
    // Re-submit task
    result = app.send_task(celery::Task("task"));
}
std::string output = result.get();
```

**Red Line 5: NEVER bypass task serialization for untrusted data**

```cpp
// BAD: Direct memory access
char buffer[1024];
auto result = app.send_task(celery::Task("process", buffer));
// Buffer overflow or injection possible
```

```cpp
// GOOD: Always serialize untrusted data
std::string safe_data = sanitize_input(untrusted_data);
auto result = app.send_task(celery::Task("process", safe_data));
```