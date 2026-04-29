# Pitfalls

**Pitfall 1: Not handling broker connection failures**

```cpp
// BAD: No connection error handling
celery::Celery app("redis://localhost:6379/0");
auto result = app.send_task(celery::Task("my_task"));
// If broker is down, this crashes
```

```cpp
// GOOD: Proper connection handling
try {
    celery::Celery app("redis://localhost:6379/0");
    app.connect(); // Explicit connection
    auto result = app.send_task(celery::Task("my_task"));
} catch (const celery::ConnectionException& e) {
    std::cerr << "Failed to connect: " << e.what() << std::endl;
    // Implement retry logic
}
```

**Pitfall 2: Ignoring task timeouts**

```cpp
// BAD: No timeout, task might hang forever
auto result = app.send_task(celery::Task("long_task"));
std::string output = result.get(); // Could block indefinitely
```

```cpp
// GOOD: Set reasonable timeouts
celery::TaskOptions opts;
opts.time_limit = 30; // 30 seconds max
opts.soft_time_limit = 25; // Warning at 25 seconds

auto result = app.send_task(celery::Task("long_task").with_options(opts));
std::string output = result.get(std::chrono::seconds(35)); // Client timeout
```

**Pitfall 3: Memory leaks with large result sets**

```cpp
// BAD: Loading entire result into memory
auto result = app.send_task(celery::Task("generate_large_data"));
std::string huge_data = result.get(); // Could consume GBs of memory
```

```cpp
// GOOD: Stream or paginate results
auto result = app.send_task(celery::Task("generate_large_data"));
celery::StreamReader reader = result.get_stream();
std::string chunk;
while (reader.read_chunk(chunk, 1024)) { // Read 1KB at a time
    process_chunk(chunk);
}
```

**Pitfall 4: Not cleaning up task results**

```cpp
// BAD: Results accumulate in backend
for (int i = 0; i < 10000; ++i) {
    auto result = app.send_task(celery::Task("my_task", i));
    // Results never cleaned up
}
```

```cpp
// GOOD: Manage result lifecycle
for (int i = 0; i < 10000; ++i) {
    auto result = app.send_task(celery::Task("my_task", i));
    std::string output = result.get();
    result.forget(); // Remove result from backend
    // Or set result expiration
}
```

**Pitfall 5: Incorrect serialization of complex types**

```cpp
// BAD: Assuming automatic serialization
struct MyData { int x; float y; };
auto result = app.send_task(celery::Task("process", MyData{1, 2.0}));
// May fail or produce incorrect results
```

```cpp
// GOOD: Explicit serialization
struct MyData { int x; float y; };
std::string json = "{\"x\":1,\"y\":2.0}";
auto result = app.send_task(celery::Task("process", json));
```

**Pitfall 6: Not handling task routing correctly**

```cpp
// BAD: All tasks go to default queue
app.send_task(celery::Task("critical_task"));
app.send_task(celery::Task("background_task"));
// Both compete for same workers
```

```cpp
// GOOD: Route tasks appropriately
celery::TaskOptions critical_opts;
critical_opts.queue = "critical";

celery::TaskOptions background_opts;
background_opts.queue = "background";

app.send_task(celery::Task("critical_task").with_options(critical_opts));
app.send_task(celery::Task("background_task").with_options(background_opts));
```