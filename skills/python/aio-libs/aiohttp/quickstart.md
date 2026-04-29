# Quickstart

```cpp
// Basic HTTP GET request
#include <aiohttp/client.h>
#include <iostream>

int main() {
    aiohttp::ClientSession session;
    auto response = session.Get("https://api.example.com/data").get();
    std::cout << "Status: " << response.status_code() << "\n";
    std::cout << "Body: " << response.text().get() << "\n";
    return 0;
}
```

```cpp
// POST request with JSON body
#include <aiohttp/client.h>
#include <nlohmann/json.hpp>

int main() {
    aiohttp::ClientSession session;
    nlohmann::json payload = {{"name", "John"}, {"age", 30}};
    
    auto response = session.Post("https://api.example.com/users", 
                                  payload.dump(), 
                                  "application/json").get();
    std::cout << "Response: " << response.text().get() << "\n";
    return 0;
}
```

```cpp
// Download file with streaming
#include <aiohttp/client.h>
#include <fstream>

int main() {
    aiohttp::ClientSession session;
    auto response = session.Get("https://example.com/largefile.zip").get();
    
    std::ofstream file("output.zip", std::ios::binary);
    auto stream = response.content();
    char buffer[8192];
    while (auto bytes_read = stream.read(buffer, sizeof(buffer))) {
        file.write(buffer, bytes_read);
    }
    return 0;
}
```

```cpp
// Custom headers and timeout
#include <aiohttp/client.h>
#include <chrono>

int main() {
    aiohttp::ClientSession session;
    aiohttp::RequestOptions opts;
    opts.timeout = std::chrono::seconds(30);
    opts.headers["Authorization"] = "Bearer token123";
    opts.headers["User-Agent"] = "MyApp/1.0";
    
    auto response = session.Get("https://api.example.com/protected", opts).get();
    std::cout << "Headers:\n";
    for (auto& [key, value] : response.headers()) {
        std::cout << key << ": " << value << "\n";
    }
    return 0;
}
```

```cpp
// Concurrent requests with futures
#include <aiohttp/client.h>
#include <future>
#include <vector>

int main() {
    aiohttp::ClientSession session;
    std::vector<std::future<aiohttp::Response>> futures;
    
    std::vector<std::string> urls = {
        "https://api1.example.com",
        "https://api2.example.com",
        "https://api3.example.com"
    };
    
    for (auto& url : urls) {
        futures.push_back(std::async(std::launch::async, [&session, url]() {
            return session.Get(url).get();
        }));
    }
    
    for (auto& future : futures) {
        auto response = future.get();
        std::cout << "Status: " << response.status_code() << "\n";
    }
    return 0;
}
```

```cpp
// Error handling with try-catch
#include <aiohttp/client.h>
#include <iostream>

int main() {
    try {
        aiohttp::ClientSession session;
        auto response = session.Get("https://invalid-url.example.com").get();
        std::cout << "Success: " << response.status_code() << "\n";
    } catch (const aiohttp::ClientError& e) {
        std::cerr << "Client error: " << e.what() << "\n";
    } catch (const aiohttp::ServerError& e) {
        std::cerr << "Server error: " << e.what() << "\n";
    } catch (const std::exception& e) {
        std::cerr << "General error: " << e.what() << "\n";
    }
    return 0;
}
```

```cpp
// Session with connection pooling
#include <aiohttp/client.h>

int main() {
    aiohttp::ClientSession session;
    session.set_connector(aiohttp::TCPConnector(10)); // Pool size 10
    
    for (int i = 0; i < 20; ++i) {
        auto response = session.Get("https://example.com").get();
        std::cout << "Request " << i << ": " << response.status_code() << "\n";
    }
    return 0;
}
```

```cpp
// WebSocket client example
#include <aiohttp/client.h>
#include <aiohttp/websocket.h>

int main() {
    aiohttp::ClientSession session;
    auto ws = session.ws_connect("wss://echo.example.com").get();
    
    ws.send("Hello, WebSocket!");
    auto msg = ws.receive().get();
    std::cout << "Received: " << msg.data() << "\n";
    
    ws.close();
    return 0;
}
```