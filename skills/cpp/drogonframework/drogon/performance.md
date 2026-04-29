# Performance

```cpp
// Use connection pooling for optimal performance
app().createDbClient("postgres", "localhost", 5432, "mydb", "user", "pass", 50); // Larger pool

// Reuse connections
auto db = app().getDbClient();
db->execSqlAsync("SELECT * FROM users",
    [](const orm::Result& result) {
        // Fast callback
    },
    [](const orm::DrogonDbException& e) {
        // Error handling
    });
```

```cpp
// Minimize memory allocations in hot paths
// BAD: Creating new strings every request
app().registerHandler("/data",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        std::string body = "Hello, World!"; // Allocation
        auto resp = HttpResponse::newHttpResponse();
        resp->setBody(std::move(body));
        callback(resp);
    },
    {Get});
```

```cpp
// GOOD: Use string views and pre-allocated buffers
static const std::string kHelloWorld = "Hello, World!";

app().registerHandler("/data",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        auto resp = HttpResponse::newHttpResponse();
        resp->setBody(kHelloWorld); // No allocation
        callback(resp);
    },
    {Get});
```

```cpp
// Use async operations to maximize throughput
// BAD: Sequential async calls
db->execSqlAsync("SELECT * FROM users",
    [db, callback](const orm::Result& users) {
        db->execSqlAsync("SELECT * FROM orders",
            [callback](const orm::Result& orders) {
                // Process both results
            },
            errorHandler);
    },
    errorHandler);
```

```cpp
// GOOD: Parallel async calls
auto usersFuture = db->execSqlAsync("SELECT * FROM users");
auto ordersFuture = db->execSqlAsync("SELECT * FROM orders");

// When both complete
whenAll(usersFuture, ordersFuture).then([callback](auto results) {
    auto& users = std::get<0>(results);
    auto& orders = std::get<1>(results);
    // Process both results
});
```