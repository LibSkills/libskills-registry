# Threading


```cpp
// Thread safety: StackTrace capture is thread-safe
#include "backward.hpp"
#include <thread>
#include <vector>

void thread_safe_capture() {
    backward::StackTrace st;
    st.load_here(32);  // Safe to call from multiple threads
    // Each thread gets its own stack trace
}

int main() {
    std::vector<std::thread> threads;
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back(thread_safe_capture);
    }
    for (auto& t : threads) t.join();
    return 0;
}
```

```cpp
// Thread safety: Printer is NOT thread-safe
#include "backward.hpp"
#include <thread>
#include <mutex>

backward::Printer global_printer;
std::mutex printer_mutex;

void safe_print() {
    backward::StackTrace st;
    st.load_here(32);
    
    // Must synchronize access to shared Printer
    std::lock_guard<std::mutex> lock(printer_mutex);
    global_printer.print(st);
}

// Better: Use thread-local Printer instances
void thread_local_print() {
    thread_local backward::Printer local_printer;
    backward::StackTrace st;
    st.load_here(32);
    local_printer.print(st);  // No synchronization needed
}

int main() {
    std::thread t1(safe_print);
    std::thread t2(thread_local_print);
    t1.join(); t2.join();
    return 0;
}
```

```cpp
// Thread safety: SignalHandling is global and NOT thread-safe
#include "backward.hpp"
#include <thread>
#include <signal.h>

// BAD - Creating SignalHandling in multiple threads
void bad_thread_setup() {
    backward::SignalHandling sh;  // Conflict with other instances
}

// GOOD - Single global instance
backward::SignalHandling global_sh;

void worker_thread() {
    // SignalHandling already installed globally
    // Just use stack traces
    backward::StackTrace st;
    st.load_here(32);
    backward::Printer().print(st);
}

int main() {
    std::thread t1(worker_thread);
    std::thread t2(worker_thread);
    t1.join(); t2.join();
    return 0;
}
```

```cpp
// Thread safety: TraceResolver is NOT thread-safe
#include "backward.hpp"
#include <thread>
#include <mutex>

class ThreadSafeResolver {
    backward::TraceResolver resolver_;
    std::mutex mutex_;
    
public:
    backward::ResolvedTrace resolve(const backward::StackTrace::Frame& frame) {
        std::lock_guard<std::mutex> lock(mutex_);
        return resolver_.resolve(frame);
    }
    
    void load_stacktrace(const backward::StackTrace& st) {
        std::lock_guard<std::mutex> lock(mutex_);
        resolver_.load_stacktrace(st);
    }
};

int main() {
    ThreadSafeResolver resolver;
    backward::StackTrace st;
    st.load_here(32);
    
    resolver.load_stacktrace(st);
    
    std::thread t1([&]() {
        auto trace = resolver.resolve(st[0]);
    });
    std::thread t2([&]() {
        auto trace = resolver.resolve(st[1]);
    });
    
    t1.join(); t2.join();
    return 0;
}
```