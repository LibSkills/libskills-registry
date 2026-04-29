# Safety

### Condition 1: Never Call Callback Multiple Times
```cpp
// BAD: Callback called twice
app().registerHandler("/data",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        auto resp = HttpResponse::newHttpResponse();
        callback(resp);
        callback(resp); // Double invocation!
    },
    {Get});
```

```cpp
// GOOD: Ensure callback is called exactly once
app().registerHandler("/data",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        auto resp = HttpResponse::newHttpResponse();
        callback(resp);
        // No further calls
    },
    {Get});
```

### Condition 2: Never Access Request After Callback
```cpp
// BAD: Using request after callback
app().registerHandler("/data",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        auto resp = HttpResponse::newHttpResponse();
        callback(resp);
        auto body = req->getBody(); // Undefined behavior!
    },
    {Get});
```

```cpp
// GOOD: Extract data before callback
app().registerHandler("/data",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        auto body = req->getBody(); // Extract first
        auto resp = HttpResponse::newHttpResponse();
        callback(resp);
    },
    {Get});
```

### Condition 3: Never Throw Exceptions in Handlers
```cpp
// BAD: Unhandled exception crashes server
app().registerHandler("/data",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        throw std::runtime_error("error"); // Crashes the event loop!
    },
    {Get});
```

```cpp
// GOOD: Handle errors gracefully
app().registerHandler("/data",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        try {
            // Risky operation
            auto resp = HttpResponse::newHttpResponse();
            callback(resp);
        } catch (const std::exception& e) {
            auto resp = HttpResponse::newHttpResponse();
            resp->setStatusCode(k500InternalServerError);
            callback(resp);
        }
    },
    {Get});
```

### Condition 4: Never Use Synchronous I/O in Async Context
```cpp
// BAD: Blocking I/O in async handler
app().registerHandler("/data",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        std::this_thread::sleep_for(std::chrono::seconds(5)); // Blocks!
        auto resp = HttpResponse::newHttpResponse();
        callback(resp);
    },
    {Get});
```

```cpp
// GOOD: Use async timers or offload to thread pool
app().registerHandler("/data",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        app().getLoop()->runAfter(5.0, [callback]() {
            auto resp = HttpResponse::newHttpResponse();
            callback(resp);
        });
    },
    {Get});
```

### Condition 5: Never Modify Shared State Without Synchronization
```cpp
// BAD: Race condition on shared counter
int globalCounter = 0;

app().registerHandler("/count",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        globalCounter++; // Race condition!
        auto resp = HttpResponse::newHttpResponse();
        callback(resp);
    },
    {Get});
```

```cpp
// GOOD: Use atomic operations
std::atomic<int> globalCounter{0};

app().registerHandler("/count",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        globalCounter.fetch_add(1);
        auto resp = HttpResponse::newHttpResponse();
        callback(resp);
    },
    {Get});
```