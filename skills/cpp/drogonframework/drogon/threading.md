# Threading

```cpp
// Thread-safe handler registration
// Drogon handles thread safety internally
app().registerHandler("/data",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        // This callback runs on the event loop thread
        // No need for external synchronization for Drogon internals
        auto resp = HttpResponse::newHttpResponse();
        callback(resp);
    },
    {Get});
```

```cpp
// Thread-safe shared state with mutex
class RequestCounter {
    std::mutex mtx;
    int count = 0;
public:
    void increment() {
        std::lock_guard<std::mutex> lock(mtx);
        ++count;
    }
    
    int get() const {
        std::lock_guard<std::mutex> lock(mtx);
        return count;
    }
};

RequestCounter counter;

app().registerHandler("/count",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        counter.increment();
        auto resp = HttpResponse::newHttpResponse();
        resp->setBody(std::to_string(counter.get()));
        callback(resp);
    },
    {Get});
```

```cpp
// Thread-safe database operations
// Drogon's DbClient is thread-safe
auto db = app().getDbClient();

// Safe to call from any thread
db->execSqlAsync("UPDATE users SET name = $1 WHERE id = $2",
    [](const orm::Result& result) {
        // Success callback
    },
    [](const orm::DrogonDbException& e) {
        // Error callback
    },
    "John", 1);
```

```cpp
// Using thread pools for CPU-intensive work
app().registerHandler("/compute",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        // Offload heavy computation to thread pool
        app().getThreadPool().runTaskAsync([callback]() {
            // CPU-intensive work here
            auto result = performHeavyComputation();
            
            // Return to event loop for response
            app().getLoop()->queueInLoop([callback, result]() {
                auto resp = HttpResponse::newHttpResponse();
                resp->setBody(result);
                callback(resp);
            });
        });
    },
    {Get});
```