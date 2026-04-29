# Best Practices

```cpp
// Use structured concurrency with scoped tasks
#include <smol/smol.hpp>
#include <smol/timer.hpp>
#include <iostream>

smol::task<void> process_request(int id) {
    auto result = co_await fetch_data(id);
    co_await save_result(result);
    std::cout << "Processed request " << id << std::endl;
}

int main() {
    smol::runtime rt;
    
    // Spawn multiple tasks and let runtime manage them
    for (int i = 0; i < 10; ++i) {
        rt.spawn(process_request(i));
    }
    
    rt.run();
    return 0;
}
```

```cpp
// Proper error handling in async code
#include <smol/smol.hpp>
#include <smol/net.hpp>
#include <iostream>
#include <expected>

smol::task<std::expected<std::string, std::error_code>> fetch_url(const std::string& url) {
    auto result = co_await smol::http::get(url);
    if (!result) {
        co_return std::unexpected(result.error());
    }
    co_return result->body;
}

int main() {
    smol::runtime rt;
    
    rt.spawn([]() -> smol::task<void> {
        auto response = co_await fetch_url("https://example.com");
        if (response) {
            std::cout << *response << std::endl;
        } else {
            std::cerr << "Error: " << response.error().message() << std::endl;
        }
    });
    
    rt.run();
    return 0;
}
```

```cpp
// Resource management with RAII wrappers
#include <smol/smol.hpp>
#include <smol/net.hpp>
#include <memory>

class AsyncResource {
    smol::TcpStream stream;
public:
    AsyncResource(smol::TcpStream s) : stream(std::move(s)) {}
    
    smol::task<void> send_data(const std::vector<char>& data) {
        co_await stream.write(data);
    }
    
    ~AsyncResource() {
        // Stream automatically closed on destruction
    }
};

int main() {
    smol::runtime rt;
    
    rt.spawn([]() -> smol::task<void> {
        auto stream = co_await smol::TcpStream::connect("127.0.0.1:8080");
        auto resource = std::make_shared<AsyncResource>(std::move(stream));
        co_await resource->send_data({'h', 'e', 'l', 'l', 'o'});
    });
    
    rt.run();
    return 0;
}
```