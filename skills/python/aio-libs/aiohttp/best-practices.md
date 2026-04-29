# Best Practices

```cpp
// Use connection pooling for optimal performance
#include <aiohttp/client.h>

class HttpClient {
public:
    HttpClient() : session_() {
        auto connector = aiohttp::TCPConnector(20); // Pool of 20 connections
        session_.set_connector(std::move(connector));
    }
    
    aiohttp::Response get(const std::string& url) {
        return session_.Get(url).get();
    }
    
private:
    aiohttp::ClientSession session_;
};
```

```cpp
// Implement retry logic with exponential backoff
#include <aiohttp/client.h>
#include <chrono>
#include <thread>

aiohttp::Response fetch_with_retry(aiohttp::ClientSession& session, 
                                    const std::string& url, 
                                    int max_retries = 3) {
    for (int attempt = 0; attempt < max_retries; ++attempt) {
        try {
            auto response = session.Get(url).get();
            if (response.status_code() < 500) {
                return response; // Success or client error
            }
        } catch (const aiohttp::ClientError&) {
            // Network error, retry
        }
        
        if (attempt < max_retries - 1) {
            std::this_thread::sleep_for(
                std::chrono::milliseconds(100 * (1 << attempt))); // Exponential backoff
        }
    }
    throw std::runtime_error("Max retries exceeded");
}
```

```cpp
// Use middleware for logging and metrics
#include <aiohttp/client.h>
#include <chrono>

class LoggingMiddleware {
public:
    aiohttp::Response operator()(aiohttp::ClientSession& session, 
                                  const std::string& url) {
        auto start = std::chrono::steady_clock::now();
        auto response = session.Get(url).get();
        auto end = std::chrono::steady_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        std::cout << "GET " << url << " -> " << response.status_code() 
                  << " (" << duration.count() << "ms)\n";
        return response;
    }
};
```

```cpp
// Proper error handling with custom exception types
#include <aiohttp/client.h>
#include <stdexcept>

class HttpException : public std::runtime_error {
public:
    HttpException(int status, const std::string& msg)
        : std::runtime_error(msg), status_(status) {}
    int status() const { return status_; }
private:
    int status_;
};

aiohttp::Response safe_request(aiohttp::ClientSession& session, 
                                const std::string& url) {
    try {
        auto response = session.Get(url).get();
        if (response.status_code() >= 400) {
            throw HttpException(response.status_code(), 
                                "HTTP error: " + std::to_string(response.status_code()));
        }
        return response;
    } catch (const aiohttp::ClientError& e) {
        throw HttpException(0, std::string("Network error: ") + e.what());
    }
}
```

```cpp
// Use streaming for large payloads
#include <aiohttp/client.h>
#include <fstream>

void download_file(aiohttp::ClientSession& session, 
                   const std::string& url, 
                   const std::string& output_path) {
    auto response = session.Get(url).get();
    if (response.status_code() != 200) {
        throw std::runtime_error("Download failed: " + 
                                 std::to_string(response.status_code()));
    }
    
    std::ofstream file(output_path, std::ios::binary);
    auto stream = response.content();
    char buffer[65536]; // 64KB buffer
    while (auto bytes = stream.read(buffer, sizeof(buffer))) {
        file.write(buffer, bytes);
    }
}
```