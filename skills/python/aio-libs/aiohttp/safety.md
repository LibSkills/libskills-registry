# Safety

### RED LINE 1: Never use a session after it has been closed
```cpp
// BAD: Using closed session
aiohttp::ClientSession session;
session.close();
auto response = session.Get("https://example.com").get(); // Undefined behavior!
```

```cpp
// GOOD: Check session state before use
aiohttp::ClientSession session;
if (session.is_open()) {
    auto response = session.Get("https://example.com").get();
} else {
    // Create new session or handle error
    aiohttp::ClientSession new_session;
    auto response = new_session.Get("https://example.com").get();
}
```

### RED LINE 2: Never ignore SSL certificate errors in production
```cpp
// BAD: Disabling SSL verification
aiohttp::ClientSession session;
aiohttp::RequestOptions opts;
opts.ssl_verify = false; // Security risk!
auto response = session.Get("https://example.com", opts).get();
```

```cpp
// GOOD: Proper SSL configuration
aiohttp::ClientSession session;
aiohttp::RequestOptions opts;
opts.ssl_verify = true; // Default, but be explicit
opts.ssl_ca_file = "/etc/ssl/certs/ca-certificates.crt";
auto response = session.Get("https://example.com", opts).get();
```

### RED LINE 3: Never mix synchronous and asynchronous calls without proper synchronization
```cpp
// BAD: Concurrent access without synchronization
aiohttp::ClientSession session;
std::thread t1([&]() { session.Get("https://api1.example.com").get(); });
std::thread t2([&]() { session.Get("https://api2.example.com").get(); });
// Race condition on session internals!
t1.join();
t2.join();
```

```cpp
// GOOD: Use proper synchronization
aiohttp::ClientSession session;
std::mutex mtx;
std::thread t1([&]() {
    std::lock_guard<std::mutex> lock(mtx);
    session.Get("https://api1.example.com").get();
});
std::thread t2([&]() {
    std::lock_guard<std::mutex> lock(mtx);
    session.Get("https://api2.example.com").get();
});
t1.join();
t2.join();
```

### RED LINE 4: Never access response data after the response object is destroyed
```cpp
// BAD: Accessing destroyed response
std::string* body_ptr = nullptr;
{
    aiohttp::ClientSession session;
    auto response = session.Get("https://example.com").get();
    body_ptr = new std::string(response.text().get());
} // response destroyed here
// body_ptr is now dangling!
```

```cpp
// GOOD: Copy data before response goes out of scope
aiohttp::ClientSession session;
auto response = session.Get("https://example.com").get();
std::string body = response.text().get(); // Copy immediately
// response can be safely destroyed now
```

### RED LINE 5: Never use default credentials or hardcoded tokens in source code
```cpp
// BAD: Hardcoded credentials
aiohttp::ClientSession session;
aiohttp::RequestOptions opts;
opts.headers["Authorization"] = "Bearer my-secret-token-12345"; // Security risk!
auto response = session.Get("https://api.example.com", opts).get();
```

```cpp
// GOOD: Use environment variables or secure config
#include <cstdlib>
aiohttp::ClientSession session;
aiohttp::RequestOptions opts;
const char* token = std::getenv("API_TOKEN");
if (token) {
    opts.headers["Authorization"] = std::string("Bearer ") + token;
} else {
    throw std::runtime_error("API_TOKEN not set");
}
auto response = session.Get("https://api.example.com", opts).get();
```