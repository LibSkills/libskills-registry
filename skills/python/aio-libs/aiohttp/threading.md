# Threading

```cpp
// Thread-safe session usage with mutex
#include <aiohttp/client.h>
#include <mutex>
#include <thread>

class ThreadSafeHttpClient {
public:
    aiohttp::Response get(const std::string& url) {
        std::lock_guard<std::mutex> lock(mutex_);
        return session_.Get(url).get();
    }
    
private:
    aiohttp::ClientSession session_;
    std::mutex mutex_;
};

void worker(ThreadSafeHttpClient& client, const std::string& url) {
    auto response = client.get(url);
    std::cout << "Thread " << std::this_thread::get_id() 
              << " got status: " << response.status_code() << "\n";
}

int main() {
    ThreadSafeHttpClient client;
    std::thread t1(worker, std::ref(client), "https://api1.example.com");
    std::thread t2(worker, std::ref(client), "https://api2.example.com");
    t1.join();
    t2.join();
    return 0;
}
```

```cpp
// Thread-local sessions for maximum concurrency
#include <aiohttp/client.h>
#include <thread>
#include <vector>

void thread_worker(int id) {
    thread_local aiohttp::ClientSession session;
    auto response = session.Get("https://example.com").get();
    std::cout << "Thread " << id << " status: " 
              << response.status_code() << "\n";
}

int main() {
    std::vector<std::thread> threads;
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back(thread_worker, i);
    }
    for (auto& t : threads) {
        t.join();
    }
    return 0;
}
```

```cpp
// Shared session with atomic operations
#include <aiohttp/client.h>
#include <atomic>
#include <thread>

class AtomicHttpClient {
public:
    aiohttp::Response get(const std::string& url) {
        auto& session = get_session();
        return session.Get(url).get();
    }
    
private:
    aiohttp::ClientSession& get_session() {
        if (!session_) {
            std::lock_guard<std::mutex> lock(init_mutex_);
            if (!session_) {
                session_ = std::make_unique<aiohttp::ClientSession>();
            }
        }
        return *session_;
    }
    
    std::unique_ptr<aiohttp::ClientSession> session_;
    std::mutex init_mutex_;
};
```

```cpp
// Thread pool with dedicated sessions
#include <aiohttp/client.h>
#include <thread>
#include <queue>
#include <functional>

class ThreadPool {
public:
    ThreadPool(size_t num_threads) {
        for (size_t i = 0; i < num_threads; ++i) {
            workers_.emplace_back([this]() {
                aiohttp::ClientSession session;
                while (true) {
                    std::function<void(aiohttp::ClientSession&)> task;
                    {
                        std::unique_lock<std::mutex> lock(queue_mutex_);
                        condition_.wait(lock, [this]() { 
                            return stop_ || !tasks_.empty(); 
                        });
                        if (stop_ && tasks_.empty()) return;
                        task = std::move(tasks_.front());
                        tasks_.pop();
                    }
                    task(session);
                }
            });
        }
    }
    
    void enqueue(std::function<void(aiohttp::ClientSession&)> task) {
        {
            std::lock_guard<std::mutex> lock(queue_mutex_);
            tasks_.push(std::move(task));
        }
        condition_.notify_one();
    }
    
private:
    std::vector<std::thread> workers_;
    std::queue<std::function<void(aiohttp::ClientSession&)>> tasks_;
    std::mutex queue_mutex_;
    std::condition_variable condition_;
    bool stop_ = false;
};
```