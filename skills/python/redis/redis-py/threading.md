# Threading

**Thread Safety Guarantees**
```cpp
#include <sw/redis++/redis++.h>
#include <thread>
#include <vector>

// Redis objects are NOT thread-safe for concurrent operations
// Each thread should have its own connection

void thread_safe_example() {
    const int NUM_THREADS = 4;
    std::vector<std::thread> threads;
    
    for (int i = 0; i < NUM_THREADS; ++i) {
        threads.emplace_back([i]() {
            // Each thread creates its own connection
            Redis redis("tcp://127.0.0.1:6379");
            
            for (int j = 0; j < 100; ++j) {
                redis.set("thread:" + std::to_string(i) + ":key:" + std::to_string(j), 
                         "value");
            }
        });
    }
    
    for (auto &t : threads) {
        t.join();
    }
}
```

**Using Connection Pool with Threads**
```cpp
class ThreadSafeRedisPool {
    std::mutex mutex;
    std::queue<std::unique_ptr<sw::redis::Redis>> pool;
    
public:
    ThreadSafeRedisPool(size_t size) {
        for (size_t i = 0; i < size; ++i) {
            pool.push(std::make_unique<sw::redis::Redis>("tcp://127.0.0.1:6379"));
        }
    }
    
    std::unique_ptr<sw::redis::Redis> acquire() {
        std::lock_guard<std::mutex> lock(mutex);
        if (pool.empty()) {
            return std::make_unique<sw::redis::Redis>("tcp://127.0.0.1:6379");
        }
        auto conn = std::move(pool.front());
        pool.pop();
        return conn;
    }
    
    void release(std::unique_ptr<sw::redis::Redis> conn) {
        std::lock_guard<std::mutex> lock(mutex);
        pool.push(std::move(conn));
    }
};
```

**Async Operations with Callbacks**
```cpp
#include <sw/redis++/redis++.h>
#include <future>

// Using futures for async operations
std::future<std::optional<std::string>> async_get(const std::string &key) {
    return std::async(std::launch::async, [key]() {
        Redis redis("tcp://127.0.0.1:6379");
        return redis.get(key);
    });
}

void async_example() {
    auto future1 = async_get("key1");
    auto future2 = async_get("key2");
    
    // Do other work while Redis operations complete
    auto result1 = future1.get();
    auto result2 = future2.get();
}
```

**Thread-Safe Pub/Sub Pattern**
```cpp
class ThreadSafeSubscriber {
    std::thread worker;
    std::atomic<bool> running{true};
    
public:
    void start() {
        worker = std::thread([this]() {
            Redis redis("tcp://127.0.0.1:6379");
            auto sub = redis.subscriber();
            
            sub.on_message([](std::string channel, std::string msg) {
                std::lock_guard<std::mutex> lock(cout_mutex);
                std::cout << channel << ": " << msg << std::endl;
            });
            
            sub.subscribe("updates");
            
            while (running) {
                try {
                    sub.consume();
                } catch (const sw::redis::Error &e) {
                    if (!running) break;
                    std::this_thread::sleep_for(std::chrono::seconds(1));
                }
            }
        });
    }
    
    void stop() {
        running = false;
        if (worker.joinable()) {
            worker.join();
        }
    }
    
private:
    static std::mutex cout_mutex;
};
```