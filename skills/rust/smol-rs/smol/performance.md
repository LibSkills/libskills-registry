# Performance

```cpp
// Understanding allocation patterns
#include <smol/smol.hpp>
#include <smol/timer.hpp>
#include <iostream>
#include <chrono>

int main() {
    smol::runtime rt;
    
    // Each spawn creates a task object (heap allocation)
    for (int i = 0; i < 1000; ++i) {
        rt.spawn([]() -> smol::task<void> {
            co_await smol::sleep(std::chrono::milliseconds(1));
        });
    }
    
    auto start = std::chrono::steady_clock::now();
    rt.run();
    auto end = std::chrono::steady_clock::now();
    
    std::cout << "Processed 1000 tasks in "
              << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count()
              << "ms" << std::endl;
    
    return 0;
}
```

```cpp
// Optimizing with batching
#include <smol/smol.hpp>
#include <smol/net.hpp>
#include <vector>
#include <iostream>

// BAD: Individual connections
smol::task<void> fetch_single(const std::string& url) {
    auto stream = co_await smol::TcpStream::connect(url);
    // Process one connection
}

// GOOD: Batch connections
smol::task<void> fetch_batch(const std::vector<std::string>& urls) {
    std::vector<smol::task<smol::TcpStream>> tasks;
    for (const auto& url : urls) {
        tasks.push_back(smol::TcpStream::connect(url));
    }
    
    // Await all connections concurrently
    for (auto& task : tasks) {
        auto stream = co_await task;
        // Process connection
    }
}

int main() {
    smol::runtime rt;
    
    std::vector<std::string> urls = {"example.com:80", "google.com:80", "github.com:80"};
    rt.spawn(fetch_batch(urls));
    rt.run();
    
    return 0;
}
```

```cpp
// Minimizing allocations with reusable buffers
#include <smol/smol.hpp>
#include <smol/net.hpp>
#include <vector>
#include <iostream>

class BufferPool {
    std::vector<std::vector<char>> buffers;
public:
    std::vector<char> acquire() {
        if (buffers.empty()) {
            return std::vector<char>(4096);
        }
        auto buf = std::move(buffers.back());
        buffers.pop_back();
        return buf;
    }
    
    void release(std::vector<char> buf) {
        buffers.push_back(std::move(buf));
    }
};

int main() {
    smol::runtime rt;
    BufferPool pool;
    
    rt.spawn([&pool]() -> smol::task<void> {
        auto buf = pool.acquire();
        auto stream = co_await smol::TcpStream::connect("example.com:80");
        co_await stream.read(buf);
        pool.release(std::move(buf));
    });
    
    rt.run();
    return 0;
}
```