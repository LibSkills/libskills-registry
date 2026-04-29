# Threading

```cpp
// 1. libuv is NOT thread-safe - all operations must happen on the event loop thread
#include <uv.h>
#include <thread>
#include <mutex>

// BAD: Calling libuv functions from different threads
void worker_thread() {
    uv_timer_t timer;
    uv_timer_init(uv_default_loop(), &timer); // CRASH: not on loop thread
}

// GOOD: Use uv_async_send to communicate with event loop
uv_async_t async;
std::mutex data_mutex;
std::string shared_data;

void async_cb(uv_async_t* handle) {
    std::lock_guard<std::mutex> lock(data_mutex);
    std::cout << "Data from worker: " << shared_data << std::endl;
}

void worker_thread() {
    {
        std::lock_guard<std::mutex> lock(data_mutex);
        shared_data = "Hello from worker";
    }
    uv_async_send(&async); // Safe to call from any thread
}

int main() {
    uv_async_init(uv_default_loop(), &async, async_cb);
    
    std::thread worker(worker_thread);
    worker.detach();
    
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}
```

```cpp
// 2. Thread pool for blocking operations
#include <uv.h>
#include <iostream>
#include <thread>

void work_cb(uv_work_t* req) {
    // This runs in a thread pool thread
    // Do blocking work here
    std::this_thread::sleep_for(std::chrono::seconds(1));
    std::cout << "Work done on thread " << std::this_thread::get_id() << std::endl;
}

void after_work_cb(uv_work_t* req, int status) {
    // This runs on the event loop thread
    std::cout << "Callback on main thread" << std::endl;
    delete req;
}

int main() {
    uv_work_t* work = new uv_work_t;
    uv_queue_work(uv_default_loop(), work, work_cb, after_work_cb);
    
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}
```

```cpp
// 3. Thread-safe handle operations with uv_async
#include <uv.h>
#include <queue>
#include <mutex>

class ThreadSafeQueue {
public:
    void push(int value) {
        std::lock_guard<std::mutex> lock(mutex_);
        queue_.push(value);
        uv_async_send(&async_);
    }
    
    void process() {
        std::lock_guard<std::mutex> lock(mutex_);
        while (!queue_.empty()) {
            int value = queue_.front();
            queue_.pop();
            // Process value on event loop thread
            std::cout << "Processing: " << value << std::endl;
        }
    }
    
    void init(uv_loop_t* loop) {
        uv_async_init(loop, &async_, [](uv_async_t* handle) {
            auto* queue = static_cast<ThreadSafeQueue*>(handle->data);
            queue->process();
        });
        async_.data = this;
    }
    
private:
    std::queue<int> queue_;
    std::mutex mutex_;
    uv_async_t async_;
};
```

```cpp
// 4. Thread-local storage for per-thread loops
#include <uv.h>
#include <thread>

thread_local uv_loop_t* tls_loop = nullptr;

void thread_function() {
    // Each thread gets its own loop
    uv_loop_t loop;
    uv_loop_init(&loop);
    tls_loop = &loop;
    
    uv_timer_t timer;
    uv_timer_init(&loop, &timer);
    uv_timer_start(&timer, [](uv_timer_t* handle) {
        std::cout << "Timer on thread " << std::this_thread::get_id() << std::endl;
    }, 1000, 0);
    
    uv_run(&loop, UV_RUN_DEFAULT);
    uv_loop_close(&loop);
}

int main() {
    std::thread t1(thread_function);
    std::thread t2(thread_function);
    
    t1.join();
    t2.join();
    return 0;
}
```

```cpp
// 5. Synchronization between threads and event loop
#include <uv.h>
#include <mutex>
#include <condition_variable>

class SyncHelper {
public:
    void wait_for_completion() {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_.wait(lock, [this]{ return completed_; });
    }
    
    void signal_completion() {
        std::lock_guard<std::mutex> lock(mutex_);
        completed_ = true;
        cv_.notify_one();
    }
    
    static void async_cb(uv_async_t* handle) {
        auto* helper = static_cast<SyncHelper*>(handle->data);
        helper->signal_completion();
    }
    
private:
    std::mutex mutex_;
    std::condition_variable cv_;
    bool completed_ = false;
};

int main() {
    SyncHelper helper;
    uv_async_t async;
    async.data = &helper;
    uv_async_init(uv_default_loop(), &async, SyncHelper::async_cb);
    
    std::thread worker([&async]() {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        uv_async_send(&async);
    });
    
    // Main thread can do other work while waiting
    uv_run(uv_default_loop(), UV_RUN_NOWAIT);
    helper.wait_for_completion();
    
    worker.join();
    uv_close((uv_handle_t*)&async, nullptr);
    return 0;
}
```