# Lifecycle

**Construction and initialization**

```cpp
#include <celery/celery.h>

// Default construction (not recommended)
celery::Celery app1; // Requires explicit initialization later

// Construction with broker URL
celery::Celery app2("redis://localhost:6379/0");

// Construction with options
celery::CeleryOptions opts;
opts.broker_url = "amqp://guest:guest@localhost:5672//";
opts.result_backend = "redis://localhost:6379/1";
opts.task_serializer = "json";
opts.result_serializer = "json";
opts.accept_content = {"json"};

celery::Celery app3(opts);

// Move construction
celery::Celery app4(std::move(app3)); // app3 is now empty
```

**Resource management and destruction**

```cpp
#include <celery/celery.h>
#include <memory>

class TaskQueueManager {
    std::unique_ptr<celery::Celery> app;
    
public:
    TaskQueueManager(const std::string& broker_url) 
        : app(std::make_unique<celery::Celery>(broker_url)) {}
    
    ~TaskQueueManager() {
        if (app) {
            app->shutdown(); // Ensure clean shutdown
        }
    }
    
    // Move semantics
    TaskQueueManager(TaskQueueManager&& other) noexcept 
        : app(std::move(other.app)) {}
    
    TaskQueueManager& operator=(TaskQueueManager&& other) noexcept {
        if (this != &other) {
            app = std::move(other.app);
        }
        return *this;
    }
    
    // No copy allowed
    TaskQueueManager(const TaskQueueManager&) = delete;
    TaskQueueManager& operator=(const TaskQueueManager&) = delete;
};
```

**Result lifecycle management**

```cpp
#include <celery/celery.h>

class ResultManager {
    celery::Celery& app;
    
public:
    celery::AsyncResult submit_task(const celery::Task& task) {
        auto result = app.send_task(task);
        result.set_expires(std::chrono::hours(24)); // Auto-cleanup
        return result;
    }
    
    void cleanup_old_results() {
        app.cleanup_results(std::chrono::hours(48)); // Remove results older than 48h
    }
    
    void forget_result(celery::AsyncResult& result) {
        result.forget(); // Remove from backend
    }
};
```

**Connection lifecycle**

```cpp
#include <celery/celery.h>

class ConnectionManager {
    celery::Celery app;
    bool connected = false;
    
public:
    void connect() {
        if (!connected) {
            app.connect();
            connected = true;
        }
    }
    
    void disconnect() {
        if (connected) {
            app.disconnect();
            connected = false;
        }
    }
    
    void reconnect() {
        disconnect();
        connect();
    }
    
    ~ConnectionManager() {
        disconnect(); // Ensure cleanup
    }
};
```