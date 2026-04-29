# Pitfalls

**Pitfall 1: Ignoring connection failures**
```cpp
// BAD: No error handling for connection
auto redis = Redis("tcp://invalid-host:6379");
redis.set("key", "value");  // Crashes or hangs

// GOOD: Handle connection errors
try {
    auto redis = Redis("tcp://127.0.0.1:6379");
    redis.set("key", "value");
} catch (const Error &e) {
    std::cerr << "Connection failed: " << e.what() << std::endl;
}
```

**Pitfall 2: Forgetting to check optional returns**
```cpp
// BAD: Assuming get always returns a value
auto val = redis.get("nonexistent");
std::cout << *val << std::endl;  // Undefined behavior if val is empty

// GOOD: Check if value exists
auto val = redis.get("nonexistent");
if (val) {
    std::cout << *val << std::endl;
} else {
    std::cout << "Key not found" << std::endl;
}
```

**Pitfall 3: Not handling timeouts properly**
```cpp
// BAD: No timeout set, can block forever
auto redis = Redis("tcp://127.0.0.1:6379");

// GOOD: Set connection and operation timeouts
ConnectionOptions opts;
opts.host = "127.0.0.1";
opts.port = 6379;
opts.connect_timeout = std::chrono::milliseconds(100);
opts.socket_timeout = std::chrono::milliseconds(500);
auto redis = Redis(opts);
```

**Pitfall 4: Memory leaks with large values**
```cpp
// BAD: Storing large binary data without care
std::string huge_data(1000000, 'x');
redis.set("large_key", huge_data);  // Copies entire string

// GOOD: Use move semantics for large data
std::string huge_data(1000000, 'x');
redis.set("large_key", std::move(huge_data));
```

**Pitfall 5: Incorrect pipeline usage**
```cpp
// BAD: Not calling exec() on pipeline
auto pipe = redis.pipeline();
pipe.set("key1", "val1");
pipe.set("key2", "val2");
// Pipeline never executed!

// GOOD: Always execute pipeline
auto pipe = redis.pipeline();
pipe.set("key1", "val1");
pipe.set("key2", "val2");
pipe.exec();
```

**Pitfall 6: Thread safety violations**
```cpp
// BAD: Sharing Redis object across threads without synchronization
Redis redis("tcp://127.0.0.1:6379");
std::thread t1([&]() { redis.set("key1", "val1"); });
std::thread t2([&]() { redis.set("key2", "val2"); });
// Data race on connection state

// GOOD: Each thread gets its own connection
std::thread t1([]() {
    Redis redis("tcp://127.0.0.1:6379");
    redis.set("key1", "val1");
});
std::thread t2([]() {
    Redis redis("tcp://127.0.0.1:6379");
    redis.set("key2", "val2");
});
```