# Threading

**Thread safety guarantees**

```cpp
#include <celery/celery.h>
#include <thread>
#include <mutex>

// Celery app is NOT thread-safe by default
celery::Celery app("redis://localhost:6379/0");
std::mutex app_mutex;

void thread_safe_submit(const celery::Task& task) {
    std::lock_guard<std::mutex> lock(app_mutex);
    app.send_task(task);
}

// Thread-safe usage
std::thread t1([&]() { thread_safe_submit(celery::Task("task1")); });
std::thread t2([&]() { thread_safe_submit(celery::Task("task2")); });
t1.join();
t2.join();
```

**Thread-local connections for performance**

```cpp
#include <celery/celery.h>
#include <thread>

class ThreadLocalCelery {
    thread_local static std::unique_ptr<celery::Celery> local_app;
    
public:
    static celery::Celery& get_instance(const std::string& broker_url) {
        if (!local_app) {
            local_app = std::make_unique<celery::Celery>(broker_url);
        }
        return *local_app;
    }
};

// Thread-safe without mutex
void worker_thread(const std::string& broker_url) {
    auto& app = ThreadLocalCelery::get_instance(broker_url);
    app.send_task(celery::Task("work"));
}
```

**Concurrent result handling**

```cpp
#include <celery/celery.h>
#include <future>
#include <vector>

class ConcurrentResultHandler {
    std::vector<std::future<std::string>> futures;
    
public:
    void submit_tasks_concurrently(celery::Celery& app, 
                                    const std::vector<celery::Task>& tasks) {
        for (const auto& task : tasks) {
            futures.push_back(std::async(std::launch::async, [&app, &task]() {
                auto result = app.send_task(task);
                return result.get();
            }));
        }
    }
    
    std::vector<std::string> collect_results() {
        std::vector<std::string> results;
        for (auto& future : futures) {
            results.push_back(future.get());
        }
        return results;
    }
};
```

**Atomic task submission**

```cpp
#include <celery/celery.h>
#include <atomic>
#include <mutex>

class AtomicTaskSubmitter {
    celery::Celery& app;
    std::mutex mtx;
    std::atomic<int> pending_tasks{0};
    
public:
    void submit_atomic(const celery::Task& task) {
        std::lock_guard<std::mutex> lock(mtx);
        app.send_task(task);
        pending_tasks.fetch_add(1);
    }
    
    void wait_for_completion() {
        while (pending_tasks.load() > 0) {
            std::this_thread::yield();
        }
    }
    
    void on_task_complete() {
        pending_tasks.fetch_sub(1);
    }
};
```

**Reader-writer lock for shared state**

```cpp
#include <celery/celery.h>
#include <shared_mutex>

class SharedTaskState {
    celery::Celery& app;
    mutable std::shared_mutex rw_mutex;
    std::unordered_map<std::string, std::string> state;
    
public:
    void update_state(const std::string& task_id, const std::string& status) {
        std::unique_lock<std::shared_mutex> lock(rw_mutex);
        state[task_id] = status;
    }
    
    std::string get_state(const std::string& task_id) const {
        std::shared_lock<std::shared_mutex> lock(rw_mutex);
        auto it = state.find(task_id);
        return it != state.end() ? it->second : "unknown";
    }
};
```