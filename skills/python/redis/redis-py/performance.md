# Performance

**Connection Pooling for High Throughput**
```cpp
// BAD: Creating new connection for each operation
void bad_performance() {
    for (int i = 0; i < 1000; ++i) {
        Redis redis("tcp://127.0.0.1:6379");  // Expensive!
        redis.set("key" + std::to_string(i), "value");
    }
}

// GOOD: Reuse connection pool
void good_performance() {
    ConnectionPoolOptions pool_opts;
    pool_opts.size = 10;
    pool_opts.wait_timeout = std::chrono::milliseconds(10);
    
    ConnectionOptions conn_opts;
    conn_opts.host = "127.0.0.1";
    conn_opts.port = 6379;
    
    Redis redis(conn_opts, pool_opts);
    
    for (int i = 0; i < 1000; ++i) {
        redis.set("key" + std::to_string(i), "value");
    }
}
```

**Pipelining for Batch Operations**
```cpp
// BAD: Individual round trips
void slow_batch() {
    Redis redis("tcp://127.0.0.1:6379");
    for (int i = 0; i < 1000; ++i) {
        redis.set("key" + std::to_string(i), "value");  // 1000 round trips
    }
}

// GOOD: Pipeline reduces round trips
void fast_batch() {
    Redis redis("tcp://127.0.0.1:6379");
    auto pipe = redis.pipeline();
    for (int i = 0; i < 1000; ++i) {
        pipe.set("key" + std::to_string(i), "value");
    }
    pipe.exec();  // Single round trip
}
```

**Memory Allocation Optimization**
```cpp
// BAD: Frequent string allocations
void bad_allocation() {
    Redis redis("tcp://127.0.0.1:6379");
    for (int i = 0; i < 10000; ++i) {
        std::string key = "user:" + std::to_string(i) + ":data";
        redis.get(key);  // New string allocation each iteration
    }
}

// GOOD: Pre-allocate and reuse buffers
void good_allocation() {
    Redis redis("tcp://127.0.0.1:6379");
    std::string key;
    key.reserve(50);  // Pre-allocate space
    
    for (int i = 0; i < 10000; ++i) {
        key = "user:" + std::to_string(i) + ":data";
        redis.get(key);
    }
}
```

**Using Bulk Operations**
```cpp
// BAD: Multiple commands for hash fields
void slow_hash_update() {
    Redis redis("tcp://127.0.0.1:6379");
    redis.hset("user:1", "name", "Alice");
    redis.hset("user:1", "age", "30");
    redis.hset("user:1", "email", "alice@example.com");
}

// GOOD: Single bulk operation
void fast_hash_update() {
    Redis redis("tcp://127.0.0.1:6379");
    std::unordered_map<std::string, std::string> fields = {
        {"name", "Alice"},
        {"age", "30"},
        {"email", "alice@example.com"}
    };
    redis.hmset("user:1", fields.begin(), fields.end());  // Single command
}
```