# Performance

**Performance characteristics**

```cpp
#include <celery/celery.h>
#include <chrono>

// Measure task submission latency
auto start = std::chrono::high_resolution_clock::now();
auto result = app.send_task(celery::Task("fast_task"));
auto end = std::chrono::high_resolution_clock::now();
auto latency = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
std::cout << "Submission latency: " << latency.count() << " μs" << std::endl;
```

**Allocation patterns and optimization**

```cpp
#include <celery/celery.h>
#include <vector>

// BAD: Frequent allocations
for (int i = 0; i < 1000; ++i) {
    auto task = celery::Task("process", std::to_string(i));
    app.send_task(task);
}

// GOOD: Reuse task objects
celery::Task base_task("process");
for (int i = 0; i < 1000; ++i) {
    auto task = base_task.with_args(std::to_string(i));
    app.send_task(task);
}
```

**Batching for high throughput**

```cpp
#include <celery/celery.h>
#include <vector>

class BatchProcessor {
    celery::Celery& app;
    std::vector<celery::Task> batch;
    size_t batch_size = 100;
    
public:
    void add_task(const celery::Task& task) {
        batch.push_back(task);
        if (batch.size() >= batch_size) {
            flush();
        }
    }
    
    void flush() {
        if (batch.empty()) return;
        app.send_tasks(batch); // Batch submission
        batch.clear();
    }
};
```

**Connection pooling for performance**

```cpp
#include <celery/celery.h>
#include <memory>

class PerformanceOptimizer {
    std::unique_ptr<celery::ConnectionPool> pool;
    
public:
    PerformanceOptimizer(const std::string& broker_url) {
        // Pool size based on expected concurrency
        pool = std::make_unique<celery::ConnectionPool>(broker_url, 
            std::thread::hardware_concurrency());
    }
    
    void submit_batch(const std::vector<celery::Task>& tasks) {
        auto conn = pool->acquire();
        conn->send_tasks(tasks);
        pool->release(std::move(conn));
    }
};
```

**Result caching for repeated queries**

```cpp
#include <celery/celery.h>
#include <unordered_map>
#include <mutex>

class ResultCache {
    std::unordered_map<std::string, std::string> cache;
    std::mutex mtx;
    
public:
    std::string get_result(celery::AsyncResult& result) {
        std::lock_guard<std::mutex> lock(mtx);
        auto it = cache.find(result.id());
        if (it != cache.end()) {
            return it->second;
        }
        
        std::string value = result.get();
        cache[result.id()] = value;
        return value;
    }
    
    void clear_cache() {
        std::lock_guard<std::mutex> lock(mtx);
        cache.clear();
    }
};
```