# Safety

**Condition 1: NEVER use a Redis object after connection failure without reconnection**
```cpp
// BAD: Using stale connection
Redis redis("tcp://127.0.0.1:6379");
// Connection drops
redis.set("key", "value");  // Throws Error

// GOOD: Reconnect on failure
try {
    redis.set("key", "value");
} catch (const Error &e) {
    redis = Redis("tcp://127.0.0.1:6379");  // Reconnect
    redis.set("key", "value");
}
```

**Condition 2: NEVER dereference an empty Optional result**
```cpp
// BAD: Dereferencing without check
auto result = redis.get("missing_key");
std::string val = *result;  // Crash if key doesn't exist

// GOOD: Always check Optional
auto result = redis.get("missing_key");
if (result) {
    std::string val = *result;
} else {
    // Handle missing key
}
```

**Condition 3: NEVER ignore transaction failures**
```cpp
// BAD: Assuming transaction always succeeds
auto tx = redis.transaction();
tx.set("key1", "val1");
tx.incr("counter");
auto results = tx.exec();  // May contain errors

// GOOD: Check transaction results
auto tx = redis.transaction();
tx.set("key1", "val1");
tx.incr("counter");
auto results = tx.exec();
for (auto &result : results) {
    if (result.is_error()) {
        std::cerr << "Transaction failed: " << result.error() << std::endl;
    }
}
```

**Condition 4: NEVER use the same connection for pub/sub and regular commands**
```cpp
// BAD: Mixed usage on same connection
Redis redis("tcp://127.0.0.1:6379");
auto sub = redis.subscriber();
sub.subscribe("channel");
redis.set("key", "value");  // Undefined behavior

// GOOD: Separate connections for pub/sub and commands
Redis cmd_redis("tcp://127.0.0.1:6379");
Redis sub_redis("tcp://127.0.0.1:6379");
auto sub = sub_redis.subscriber();
sub.subscribe("channel");
cmd_redis.set("key", "value");
```

**Condition 5: NEVER ignore memory allocation failures for large operations**
```cpp
// BAD: No size limits
std::string data = redis.get("huge_key");  // Could allocate GBs

// GOOD: Use streaming or size checks
auto result = redis.get("huge_key");
if (result && result->size() > 1000000) {
    throw std::runtime_error("Value too large");
}
```