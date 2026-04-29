# Pitfalls

### BAD: Not handling response body properly
```cpp
// BAD: Ignoring response body can leak resources
aiohttp::ClientSession session;
auto response = session.Get("https://example.com").get();
// Response body not consumed - connection may not be reusable
```

```cpp
// GOOD: Always consume or close response body
aiohttp::ClientSession session;
auto response = session.Get("https://example.com").get();
std::string body = response.text().get(); // Consumes body
// Or: response.close(); // Explicitly close
```

### BAD: Using session after destruction
```cpp
// BAD: Dangling reference to destroyed session
aiohttp::Response* resp_ptr = nullptr;
{
    aiohttp::ClientSession session;
    auto response = session.Get("https://example.com").get();
    resp_ptr = &response; // Pointer to temporary
}
// resp_ptr is now dangling!
```

```cpp
// GOOD: Keep session alive while using responses
aiohttp::ClientSession session;
auto response = session.Get("https://example.com").get();
// Use response while session is alive
std::string body = response.text().get();
```

### BAD: Ignoring timeout settings
```cpp
// BAD: Default timeout may be too long
aiohttp::ClientSession session;
// Could hang indefinitely on slow server
auto response = session.Get("https://slow.example.com").get();
```

```cpp
// GOOD: Set appropriate timeouts
aiohttp::ClientSession session;
aiohttp::RequestOptions opts;
opts.timeout = std::chrono::seconds(10);
opts.connect_timeout = std::chrono::seconds(5);
auto response = session.Get("https://slow.example.com", opts).get();
```

### BAD: Not checking response status
```cpp
// BAD: Assuming request always succeeds
aiohttp::ClientSession session;
auto response = session.Get("https://api.example.com/data").get();
auto data = response.json().get(); // May throw if status is 404
```

```cpp
// GOOD: Check status before processing
aiohttp::ClientSession session;
auto response = session.Get("https://api.example.com/data").get();
if (response.status_code() == 200) {
    auto data = response.json().get();
} else {
    std::cerr << "Error: " << response.status_code() << "\n";
}
```

### BAD: Creating new session for each request
```cpp
// BAD: Inefficient - no connection reuse
for (int i = 0; i < 100; ++i) {
    aiohttp::ClientSession session;
    auto response = session.Get("https://example.com").get();
}
```

```cpp
// GOOD: Reuse session for multiple requests
aiohttp::ClientSession session;
for (int i = 0; i < 100; ++i) {
    auto response = session.Get("https://example.com").get();
}
```

### BAD: Not handling redirects properly
```cpp
// BAD: Default may follow redirects without control
aiohttp::ClientSession session;
auto response = session.Get("https://example.com/redirect").get();
// May have followed multiple redirects
```

```cpp
// GOOD: Configure redirect behavior
aiohttp::ClientSession session;
aiohttp::RequestOptions opts;
opts.max_redirects = 3; // Limit redirects
opts.follow_redirects = true;
auto response = session.Get("https://example.com/redirect", opts).get();
```

### BAD: Memory leak with large responses
```cpp
// BAD: Loading entire response into memory
aiohttp::ClientSession session;
auto response = session.Get("https://example.com/largefile").get();
std::string huge_data = response.text().get(); // May crash with large files
```

```cpp
// GOOD: Stream large responses
aiohttp::ClientSession session;
auto response = session.Get("https://example.com/largefile").get();
auto stream = response.content();
char buffer[4096];
while (auto bytes = stream.read(buffer, sizeof(buffer))) {
    process_chunk(buffer, bytes); // Process incrementally
}
```