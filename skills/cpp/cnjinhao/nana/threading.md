# Threading

**Thread Safety Guarantees**

Nana's GUI widgets are NOT thread-safe. All widget operations must be performed from the main thread where the event loop runs. The library provides `nana::internal_scope_guard` for internal synchronization, but user code should not rely on it for widget access.

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/label.hpp>
#include <nana/gui/timer.hpp>
#include <thread>
#include <atomic>
#include <queue>
#include <mutex>

// Safe pattern: Use atomic flags and timer for thread communication
class ThreadSafeUpdater {
    nana::form fm;
    nana::label status;
    nana::timer update_timer;
    std::atomic<bool> data_ready{false};
    std::string pending_data;
    std::mutex data_mutex;
    
public:
    ThreadSafeUpdater()
        : fm(nana::size(300, 100))
        , status(fm, nana::rectangle(10, 10, 280, 80))
        , update_timer()
    {
        fm.caption("Thread Safe Updater");
        status.caption("Waiting for data...");
        
        // Timer polls for updates on main thread
        update_timer.elapse([this]() {
            if (data_ready.load()) {
                std::lock_guard<std::mutex> lock(data_mutex);
                status.caption(pending_data);
                data_ready.store(false);
            }
        });
        update_timer.interval(std::chrono::milliseconds(50));
        update_timer.start();
        
        // Start worker thread
        std::thread worker([this]() {
            worker_thread();
        });
        worker.detach();
        
        fm.show();
    }
    
    void run() { nana::exec(); }
    
private:
    void worker_thread() {
        for (int i = 0; i < 5; ++i) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
            
            std::lock_guard<std::mutex> lock(data_mutex);
            pending_data = "Update " + std::to_string(i + 1);
            data_ready.store(true);
        }
    }
};
```

**Concurrent Data Access**

When sharing data between threads and the GUI, use proper synchronization primitives.

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/label.hpp>
#include <nana/gui/timer.hpp>
#include <thread>
#include <mutex>
#include <queue>
#include <string>

class ThreadSafeQueue {
    nana::form fm;
    nana::label display;
    nana::timer consumer;
    std::queue<std::string> message_queue;
    std::mutex queue_mutex;
    std::atomic<bool> running{true};
    
public:
    ThreadSafeQueue()
        : fm(nana::size(400, 200))
        , display(fm, nana::rectangle(10, 10, 380, 180))
        , consumer()
    {
        fm.caption("Thread Safe Queue");
        display.caption("Messages will appear here");
        
        // Consumer timer runs on main thread
        consumer.elapse([this]() {
            consume_messages();
        });
        consumer.interval(std::chrono::milliseconds(100));
        consumer.start();
        
        // Producer threads
        for (int i = 0; i < 3; ++i) {
            std::thread producer([this, i]() {
                produce_messages(i);
            });
            producer.detach();
        }
        
        fm.show();
    }
    
    void run() { nana::exec(); }
    
private:
    void produce_messages(int producer_id) {
        for (int i = 0; i < 5; ++i) {
            std::this_thread::sleep_for(std::chrono::milliseconds(200 + rand() % 300));
            
            std::lock_guard<std::mutex> lock(queue_mutex);
            message_queue.push("Producer " + std::to_string(producer_id) + 
                              ": Message " + std::to_string(i));
        }
    }
    
    void consume_messages() {
        std::lock_guard<std::mutex> lock(queue_mutex);
        while (!message_queue.empty()) {
            std::string msg = message_queue.front();
            message_queue.pop();
            display.caption(msg + "\n" + display.caption());
        }
    }
};
```

**Using `nana::internal_scope_guard`**

For advanced use cases, Nana provides `nana::internal_scope_guard` for thread-safe access to internal data structures. This should be used sparingly and only when necessary.

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/label.hpp>
#include <nana/gui/timer.hpp>
#include <thread>
#include <mutex>

class AdvancedThreading {
    nana::form fm;
    nana::label counter_label;
    nana::timer update_timer;
    int shared_counter = 0;
    std::mutex counter_mutex;
    
public:
    AdvancedThreading()
        : fm(nana::size(300, 100))
        , counter_label(fm, nana::rectangle(10, 10, 280, 80))
        , update_timer()
    {
        fm.caption("Advanced Threading");
        counter_label.caption("Counter: 0");
        
        // Timer for safe UI updates
        update_timer.elapse([this]() {
            std::lock_guard<std::mutex> lock(counter_mutex);
            counter_label.caption("Counter: " + std::to_string(shared_counter));
        });
        update_timer.interval(std::chrono::milliseconds(100));
        update_timer.start();
        
        // Multiple worker threads
        for (int i = 0; i < 4; ++i) {
            std::thread([this]() {
                for (int j = 0; j < 25; ++j) {
                    std::this_thread::sleep_for(std::chrono::milliseconds(50 + rand() % 100));
                    {
                        std::lock_guard<std::mutex> lock(counter_mutex);
                        ++shared_counter;
                    }
                }
            }).detach();
        }
        
        fm.show();
    }
    
    void run() { nana::exec(); }
};
```

**Thread Pool Pattern**

For heavy computations, use a thread pool and communicate results back to the GUI thread.

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/label.hpp>
#include <nana/gui/timer.hpp>
#include <nana/gui/widgets/progress.hpp>
#include <thread>
#include <mutex>
#include <vector>
#include <functional>
#include <queue>

class ThreadPoolGUI {
    nana::form fm;
    nana::label status;
    nana::progress progress_bar;
    nana::timer result_poller;
    
    std::vector<std::thread> workers;
    std::queue<std::function<void()>> tasks;
    std::queue<std::string> results;
    std::mutex task_mutex;
    std::mutex result_mutex;
    std::atomic<int> completed_tasks{0};
    int total_tasks = 10;
    
public:
    ThreadPoolGUI()
        : fm(nana::size(400, 150))
        , status(fm, nana::rectangle(10, 10, 380, 30))
        , progress_bar(fm, nana::rectangle(10, 50, 380, 30))
        , result_poller()
    {
        fm.caption("Thread Pool GUI");
        status.caption("Processing...");
        progress_bar.amount(total_tasks);
        progress_bar.value(0);
        
        // Start worker threads
        int num_threads = std::thread::hardware_concurrency();
        for (int i = 0; i < num_threads; ++i) {
            workers.emplace_back([this]() { worker_loop(); });
        }
        
        // Add tasks
        for (int i = 0; i < total_tasks; ++i) {
            add_task([i]() {
                std::this_thread::sleep_for(std::chrono::milliseconds(100 + rand() % 200));
                return "Task " + std::to_string(i) + " completed";
            });
        }
        
        // Poll for results on main thread
        result_poller.elapse([this]() {
            check_results();
        });
        result_poller.interval(std::chrono::milliseconds(50));
        result_poller.start();
        
        fm.show();
    }
    
    void run() { nana::exec(); }
    
    ~ThreadPoolGUI() {
        for (auto& t : workers) {
            if (t.joinable()) t.join();
        }
    }
    
private:
    void add_task(std::function<std::string()> task) {
        std::lock_guard<std::mutex> lock(task_mutex);
        tasks.push(std::move(task));
    }
    
    void worker_loop() {
        while (completed_tasks < total_tasks) {
            std::function<std::string()> task;
            {
                std::lock_guard<std::mutex> lock(task_mutex);
                if (tasks.empty()) {
                    std::this_thread::sleep_for(std::chrono::milliseconds(10));
                    continue;
                }
                task = std::move(tasks.front());
                tasks.pop();
            }
            
            std::string result = task();
            
            {
                std::lock_guard<std::mutex> lock(result_mutex);
                results.push(std::move(result));
            }
            completed_tasks.fetch_add(1);
        }
    }
    
    void check_results() {
        std::lock_guard<std::mutex> lock(result_mutex);
        while (!results.empty()) {
            status.caption(results.front());
            results.pop();
            progress_bar.value(progress_bar.value() + 1);
        }
        
        if (completed_tasks >= total_tasks && results.empty()) {
            status.caption("All tasks completed!");
            result_poller.stop();
        }
    }
};
```