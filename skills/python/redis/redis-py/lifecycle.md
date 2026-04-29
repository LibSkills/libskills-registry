# Lifecycle

**Construction and Connection Management**
```cpp
#include <sw/redis++/redis++.h>

// Default construction (no connection)
sw::redis::Redis redis;  // Not connected

// Construction with connection string
sw::redis::Redis redis1("tcp://127.0.0.1:6379");

// Construction with options
sw::redis::ConnectionOptions opts;
opts.host = "127.0.0.1";
opts.port = 6379;
opts.password = "secret";
opts.db = 1;  // Select database 1
sw::redis::Redis redis2(opts);

// Construction with connection pool
sw::redis::ConnectionPoolOptions pool_opts;
pool_opts.size = 5;
sw::redis::Redis redis3(opts, pool_opts);
```

**Destruction and Resource Cleanup**
```cpp
void resource_management() {
    // Redis object automatically closes connection on destruction
    {
        sw::redis::Redis redis("tcp://127.0.0.1:6379");
        redis.set("temp", "data");
    }  // Connection closed here
    
    // For explicit cleanup, use reset or let it go out of scope
    auto redis = std::make_unique<sw::redis::Redis>("tcp://127.0.0.1:6379");
    redis->set("key", "value");
    redis.reset();  // Explicitly close connection
}
```

**Move Semantics**
```cpp
void move_example() {
    sw::redis::Redis redis1("tcp://127.0.0.1:6379");
    redis1.set("key", "value");
    
    // Move constructor - transfers connection ownership
    sw::redis::Redis redis2(std::move(redis1));
    // redis1 is now in valid but unspecified state
    
    // Move assignment
    sw::redis::Redis redis3;
    redis3 = std::move(redis2);
    
    // After move, original object can be reused
    redis1 = sw::redis::Redis("tcp://127.0.0.1:6379");  // New connection
}
```

**Connection Pool Lifecycle**
```cpp
class ConnectionPoolManager {
    std::unique_ptr<sw::redis::Redis> pool;
    
public:
    ConnectionPoolManager() {
        sw::redis::ConnectionPoolOptions pool_opts;
        pool_opts.size = 10;
        pool_opts.wait_timeout = std::chrono::milliseconds(100);
        pool_opts.connection_lifetime = std::chrono::minutes(5);  // Auto-recycle
        
        sw::redis::ConnectionOptions conn_opts;
        conn_opts.host = "127.0.0.1";
        conn_opts.port = 6379;
        
        pool = std::make_unique<sw::redis::Redis>(conn_opts, pool_opts);
    }
    
    ~ConnectionPoolManager() {
        pool.reset();  // Clean up all connections
    }
    
    // Prevent copying
    ConnectionPoolManager(const ConnectionPoolManager&) = delete;
    ConnectionPoolManager& operator=(const ConnectionPoolManager&) = delete;
    
    // Allow moving
    ConnectionPoolManager(ConnectionPoolManager&&) = default;
    ConnectionPoolManager& operator=(ConnectionPoolManager&&) = default;
};
```