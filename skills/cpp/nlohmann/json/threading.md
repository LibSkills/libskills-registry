# nlohmann/json — Threading

## No Internal Synchronization

`json` types contain no mutexes or atomic operations. They are NOT thread-safe for concurrent modification.

| Operation | Thread-safe? | Notes |
|-----------|-------------|-------|
| Read-only access (const methods) | Yes | Multiple readers are safe |
| Concurrent const access on same object | Yes | Standard C++ const concurrency |
| Non-const access (assign, insert, erase) | **No** | Must be externally synchronized |
| Concurrent read + write on same object | **No** | Data race |
| `dump()` on const ref | Yes | No modifications, safe |
| `parse()` on distinct inputs | Yes | Each call is independent |
| Copy/move assignment | **No** | Modify internal state |

## Read-Only Sharing

Multiple threads can safely read the same `const json` object simultaneously:

```cpp
const json config = load_config();

// Multiple reader threads — safe
std::thread t1([&]{
    std::cout << config.dump(2);
});
std::thread t2([&]{
    int port = config.value("port", 8080);
});
t1.join(); t2.join();
```

## Write Synchronization

Concurrent modifications require external synchronization:

```cpp
json shared;
std::mutex mtx;

void thread_safe_update(const std::string& key, int value) {
    std::lock_guard<std::mutex> lock(mtx);
    shared[key] = value;
}
```

## Per-Thread Instances

The safest pattern for concurrent use is one `json` per thread:

```cpp
void worker(int id) {
    json j; // local to this thread
    j["thread_id"] = id;
    j["data"] = compute();
    // serialize or pass the result out thread-safe
}
```

## `json::parse()` Thread Safety

`parse()` is safe to call concurrently on different input strings. Internal allocations are standard heap operations (thread-safe on modern allocators).

```cpp
// Safe: each parse is independent
auto future1 = std::async([&]{ return json::parse(str1); });
auto future2 = std::async([&]{ return json::parse(str2); });
```

## SAX Parsing in Threads

Each `sax_parse()` call operates on its own stream and handler. Concurrent calls to `sax_parse()` with different handler objects are safe; sharing handler state across threads is NOT.
