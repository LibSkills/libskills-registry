# Performance

```cpp
// Connection pooling reduces overhead
#include <aiohttp/client.h>
#include <chrono>

void benchmark_pooling() {
    auto start = std::chrono::steady_clock::now();
    
    // Without pooling (BAD)
    for (int i = 0; i < 100; ++i) {
        aiohttp::ClientSession session;
        session.Get("https://example.com").get();
    }
    auto without_pool = std::chrono::steady_clock::now() - start;
    
    // With pooling (GOOD)
    start = std::chrono::steady_clock::now();
    aiohttp::ClientSession session;
    session.set_connector(aiohttp::TCPConnector(10));
    for (int i = 0; i < 100; ++i) {
        session.Get("https://example.com").get();
    }
    auto with_pool = std::chrono::steady_clock::now() - start;
    
    std::cout << "Without pool: " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(without_pool).count()
              << "ms\n";
    std::cout << "With pool: " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(with_pool).count()
              << "ms\n";
}
```

```cpp
// Buffer size optimization for streaming
#include <aiohttp/client.h>

void optimal_streaming(aiohttp::ClientSession& session) {
    auto response = session.Get("https://example.com/largefile").get();
    auto stream = response.content();
    
    // Use larger buffer for better throughput
    const size_t buffer_size = 65536; // 64KB optimal for most systems
    char* buffer = new char[buffer_size];
    
    while (auto bytes = stream.read(buffer, buffer_size)) {
        process_data(buffer, bytes);
    }
    delete[] buffer;
}
```

```cpp
// Pre-allocate response buffers for known sizes
#include <aiohttp/client.h>
#include <vector>

void preallocated_response(aiohttp::ClientSession& session) {
    auto response = session.Get("https://example.com/data").get();
    
    // If content-length is known, pre-allocate
    auto content_length = response.headers().find("Content-Length");
    if (content_length != response.headers().end()) {
        size_t size = std::stoul(content_length->second);
        std::vector<char> buffer(size);
        response.content().read(buffer.data(), size);
    }
}
```

```cpp
// Batch requests for better throughput
#include <aiohttp/client.h>
#include <future>
#include <vector>

std::vector<aiohttp::Response> batch_requests(
    aiohttp::ClientSession& session,
    const std::vector<std::string>& urls) {
    
    std::vector<std::future<aiohttp::Response>> futures;
    futures.reserve(urls.size());
    
    for (const auto& url : urls) {
        futures.push_back(std::async(std::launch::async, [&session, url]() {
            return session.Get(url).get();
        }));
    }
    
    std::vector<aiohttp::Response> responses;
    responses.reserve(urls.size());
    for (auto& future : futures) {
        responses.push_back(future.get());
    }
    return responses;
}
```