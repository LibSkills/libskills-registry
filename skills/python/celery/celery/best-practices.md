# Best Practices

**Practice 1: Use connection pooling for high-throughput applications**

```cpp
#include <celery/celery.h>
#include <memory>

class TaskManager {
    std::unique_ptr<celery::ConnectionPool> pool;
public:
    TaskManager(const std::string& broker_url) {
        pool = std::make_unique<celery::ConnectionPool>(broker_url, 10); // 10 connections
    }
    
    void submit_task(const celery::Task& task) {
        auto conn = pool->acquire();
        conn->send_task(task);
        pool->release(std::move(conn));
    }
};
```

**Practice 2: Implement retry logic with exponential backoff**

```cpp
#include <celery/celery.h>
#include <chrono>
#include <thread>

class ReliableTaskSubmitter {
    celery::Celery& app;
    int max_retries = 3;
    
public:
    celery::AsyncResult submit_with_retry(const celery::Task& task) {
        for (int i = 0; i < max_retries; ++i) {
            try {
                return app.send_task(task);
            } catch (const celery::ConnectionException&) {
                if (i == max_retries - 1) throw;
                std::this_thread::sleep_for(std::chrono::seconds(1 << i)); // Exponential backoff
            }
        }
        throw std::runtime_error("Failed to submit task");
    }
};
```

**Practice 3: Use task priorities for critical workloads**

```cpp
#include <celery/celery.h>

class PriorityTaskManager {
    celery::Celery& app;
    
public:
    void submit_critical(const std::string& name, const std::string& data) {
        celery::TaskOptions opts;
        opts.priority = 10; // High priority
        opts.queue = "critical";
        app.send_task(celery::Task(name, data).with_options(opts));
    }
    
    void submit_background(const std::string& name, const std::string& data) {
        celery::TaskOptions opts;
        opts.priority = 1; // Low priority
        opts.queue = "background";
        app.send_task(celery::Task(name, data).with_options(opts));
    }
};
```

**Practice 4: Monitor task execution with callbacks**

```cpp
#include <celery/celery.h>
#include <functional>

class MonitoredTask {
    celery::Celery& app;
    std::function<void(const std::string&)> on_success;
    std::function<void(const std::exception&)> on_failure;
    
public:
    void execute(const celery::Task& task) {
        auto result = app.send_task(task);
        result.on_complete([this](const std::string& output) {
            on_success(output);
        });
        result.on_error([this](const std::exception& e) {
            on_failure(e);
        });
    }
};
```

**Practice 5: Implement graceful shutdown**

```cpp
#include <celery/celery.h>
#include <atomic>
#include <csignal>

class GracefulShutdown {
    celery::Celery& app;
    std::atomic<bool> running{true};
    
public:
    void run() {
        signal(SIGINT, [](int) { running = false; });
        
        while (running) {
            try {
                auto tasks = app.consume_tasks();
                for (auto& task : tasks) {
                    if (!running) break;
                    process_task(task);
                }
            } catch (const celery::ShutdownException&) {
                break;
            }
        }
        
        app.shutdown(); // Wait for in-flight tasks
    }
};
```