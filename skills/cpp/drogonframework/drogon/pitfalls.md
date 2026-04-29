# Pitfalls

### Pitfall 1: Blocking the Event Loop
```cpp
// BAD: Synchronous database call blocks the event loop
app().registerHandler("/users",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        auto db = app().getDbClient();
        auto result = db->execSqlSync("SELECT * FROM users"); // Blocks!
        auto resp = HttpResponse::newHttpJsonResponse(resultToJson(result));
        callback(resp);
    },
    {Get});
```

```cpp
// GOOD: Use asynchronous database operations
app().registerHandler("/users",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        auto db = app().getDbClient();
        db->execSqlAsync("SELECT * FROM users",
            [callback](const orm::Result& result) {
                auto resp = HttpResponse::newHttpJsonResponse(resultToJson(result));
                callback(resp);
            },
            [callback](const orm::DrogonDbException& e) {
                auto resp = HttpResponse::newHttpResponse();
                resp->setStatusCode(k500InternalServerError);
                callback(resp);
            });
    },
    {Get});
```

### Pitfall 2: Capturing Raw Pointers in Lambdas
```cpp
// BAD: Raw pointer capture can lead to dangling references
app().registerHandler("/data",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        auto* data = new std::string("some data"); // Raw pointer
        someAsyncOperation([data, callback]() {
            callback(HttpResponse::newHttpResponse());
            delete data; // May crash if callback is delayed
        });
    },
    {Get});
```

```cpp
// GOOD: Use shared_ptr or capture by value
app().registerHandler("/data",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        auto data = std::make_shared<std::string>("some data");
        someAsyncOperation([data, callback]() {
            callback(HttpResponse::newHttpResponse());
        });
    },
    {Get});
```

### Pitfall 3: Incorrect Response Status Codes
```cpp
// BAD: Missing status code for error responses
app().registerHandler("/api/user",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        auto json = req->getJsonObject();
        if (!json) {
            auto resp = HttpResponse::newHttpResponse();
            resp->setBody("Bad request");
            callback(resp); // Defaults to 200 OK!
        }
    },
    {Post});
```

```cpp
// GOOD: Always set appropriate status codes
app().registerHandler("/api/user",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        auto json = req->getJsonObject();
        if (!json) {
            auto resp = HttpResponse::newHttpResponse();
            resp->setStatusCode(k400BadRequest);
            resp->setBody("Bad request");
            callback(resp);
        }
    },
    {Post});
```

### Pitfall 4: Not Handling WebSocket Close Properly
```cpp
// BAD: Ignoring WebSocket close events
class MyWebSocket : public WebSocketController {
    void handleNewMessage(const WebSocketConnectionPtr& wsConn,
                          std::string&& message,
                          const WebSocketMessageType& type) override {
        wsConn->send(message); // May crash if connection closed
    }
};
```

```cpp
// GOOD: Check connection state before sending
class MyWebSocket : public WebSocketController {
    void handleNewMessage(const WebSocketConnectionPtr& wsConn,
                          std::string&& message,
                          const WebSocketMessageType& type) override {
        if (wsConn->connected()) {
            wsConn->send(message);
        }
    }
    
    void handleConnectionClosed(const WebSocketConnectionPtr& wsConn) override {
        // Clean up resources
    }
};
```

### Pitfall 5: Memory Leaks with Shared Resources
```cpp
// BAD: Circular references in shared_ptr chains
class SessionManager {
    std::unordered_map<std::string, std::shared_ptr<Session>> sessions;
};

class Session {
    std::shared_ptr<SessionManager> manager; // Circular reference!
};
```

```cpp
// GOOD: Use weak_ptr to break cycles
class SessionManager {
    std::unordered_map<std::string, std::shared_ptr<Session>> sessions;
};

class Session {
    std::weak_ptr<SessionManager> manager; // Break the cycle
};
```

### Pitfall 6: Ignoring Thread Safety in Callbacks
```cpp
// BAD: Shared state without synchronization
std::unordered_map<std::string, int> requestCounts;

app().registerHandler("/count",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        requestCounts["total"]++; // Not thread-safe!
        auto resp = HttpResponse::newHttpResponse();
        callback(resp);
    },
    {Get});
```

```cpp
// GOOD: Use thread-safe data structures
std::shared_mutex mtx;
std::unordered_map<std::string, int> requestCounts;

app().registerHandler("/count",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        {
            std::lock_guard<std::shared_mutex> lock(mtx);
            requestCounts["total"]++;
        }
        auto resp = HttpResponse::newHttpResponse();
        callback(resp);
    },
    {Get});
```