# Lifecycle

```cpp
// Construction with default settings
#include <aiohttp/client.h>

aiohttp::ClientSession session; // Default constructor
// Session is ready to use immediately
```

```cpp
// Construction with custom configuration
aiohttp::ClientSession session;
session.set_connector(aiohttp::TCPConnector(5)); // Pool size
session.set_cookie_jar(aiohttp::CookieJar()); // Enable cookies
session.set_default_headers({{"User-Agent", "MyApp/1.0"}});
```

```cpp
// Move semantics - sessions are movable but not copyable
aiohttp::ClientSession session1;
session1.Get("https://example.com").get(); // Use session1

aiohttp::ClientSession session2 = std::move(session1); // Move
// session1 is now in valid but unspecified state
session2.Get("https://example.org").get(); // Use session2
```

```cpp
// Proper destruction and cleanup
{
    aiohttp::ClientSession session;
    // ... use session ...
} // session automatically closes all connections and releases resources

// Explicit close
aiohttp::ClientSession session;
session.Get("https://example.com").get();
session.close(); // Force close all connections
```

```cpp
// Resource management with RAII
class HttpClientManager {
public:
    HttpClientManager() : session_() {
        // Initialize with optimal settings
        auto connector = aiohttp::TCPConnector(10);
        session_.set_connector(std::move(connector));
    }
    
    ~HttpClientManager() {
        session_.close(); // Ensure cleanup
    }
    
    // Move constructor
    HttpClientManager(HttpClientManager&& other) noexcept 
        : session_(std::move(other.session_)) {}
    
    // No copy
    HttpClientManager(const HttpClientManager&) = delete;
    HttpClientManager& operator=(const HttpClientManager&) = delete;
    
private:
    aiohttp::ClientSession session_;
};
```