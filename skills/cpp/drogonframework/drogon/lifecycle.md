# Lifecycle

```cpp
// Proper construction of Drogon application
#include <drogon/drogon.h>

int main() {
    // Configure before running
    app().setLogPath("./logs");
    app().setLogLevel(trantor::Logger::kDebug);
    app().setStaticFilesPath("./static");
    app().addListener("0.0.0.0", 8080);
    
    // Register handlers
    app().registerHandler("/health", 
        [](const HttpRequestPtr& req,
           std::function<void(const HttpResponsePtr&)>&& callback) {
            auto resp = HttpResponse::newHttpResponse();
            resp->setBody("OK");
            callback(resp);
        },
        {Get});
    
    // Start the event loop
    app().run();
    return 0;
}
```

```cpp
// Resource management with RAII
class DatabaseConnection {
    std::shared_ptr<orm::DbClient> client;
public:
    DatabaseConnection() {
        client = app().getDbClient();
        if (!client) {
            throw std::runtime_error("Database not configured");
        }
    }
    
    ~DatabaseConnection() {
        // Connection returned to pool automatically
    }
    
    // Move semantics
    DatabaseConnection(DatabaseConnection&& other) noexcept
        : client(std::move(other.client)) {}
    
    DatabaseConnection& operator=(DatabaseConnection&& other) noexcept {
        if (this != &other) {
            client = std::move(other.client);
        }
        return *this;
    }
    
    // Prevent copying
    DatabaseConnection(const DatabaseConnection&) = delete;
    DatabaseConnection& operator=(const DatabaseConnection&) = delete;
};
```

```cpp
// Proper shutdown sequence
int main() {
    app().registerPreQuitAdvice([]() {
        LOG_INFO << "Server shutting down...";
        // Clean up resources
    });
    
    app().registerPostQuitAdvice([]() {
        LOG_INFO << "Server shutdown complete";
    });
    
    app().addListener("0.0.0.0", 8080).run();
}
```