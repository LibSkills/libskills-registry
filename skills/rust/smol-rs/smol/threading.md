# Threading

```cpp
// Single-threaded execution model
#include <smol/smol.hpp>
#include <thread>
#include <iostream>

int main() {
    smol::runtime rt;
    
    rt.spawn([]() {
        std::cout << "Running on thread: "
                  << std::this_thread::get_id() << std::endl;
    });
    
    rt.spawn([]() {
        std::cout << "Also on same thread: "
                  << std::this_thread::get_id() << std::endl;
    });
    
    rt.run(); // Both tasks run on the calling thread
    return 0;
}
```

```cpp
// Thread-local storage with smol
#include <smol/smol.hpp>
#include <iostream>
#include <thread>

thread_local int tls_value = 0;

int main() {
    smol::runtime rt;
    
    rt.spawn([]() {
        tls_value = 42;
        std::cout << "TLS value: " << tls_value << std::endl;
    });
    
    // TLS is safe because all tasks run on same thread
    rt.spawn([]() {
        std::cout << "Same TLS value: " << tls_value << std::endl;
    });
    
    rt.run();
    return 0;
}
```

```cpp
// Multi-runtime pattern for multi-threading
#include <smol/smol.hpp>
#include <thread>
#include <vector>
#include <iostream>

void worker_thread(int id) {
    smol::runtime local_rt;
    
    local_rt.spawn([id]() {
        std::cout << "Worker " << id << " on thread "
                  << std::this_thread::get_id() << std::endl;
    });
    
    local_rt.run();
}

int main() {
    std::vector<std::thread> threads;
    
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back(worker_thread, i);
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    return 0;
}
```

```cpp
// Channel communication between runtimes (via shared state)
#include <smol/smol.hpp>
#include <thread>
#include <mutex>
#include <queue>
#include <iostream>

struct SharedChannel {
    std::mutex mtx;
    std::queue<int> messages;
    std::condition_variable cv;
};

int main() {
    SharedChannel channel;
    
    std::thread producer([&channel]() {
        smol::runtime rt;
        
        rt.spawn([&channel]() -> smol::task<void> {
            // Simulate async work
            co_await smol::sleep(std::chrono::milliseconds(100));
            
            std::lock_guard<std::mutex> lock(channel.mtx);
            channel.messages.push(42);
            channel.cv.notify_one();
        });
        
        rt.run();
    });
    
    std::thread consumer([&channel]() {
        smol::runtime rt;
        
        rt.spawn([&channel]() -> smol::task<void> {
            std::unique_lock<std::mutex> lock(channel.mtx);
            channel.cv.wait(lock, [&channel]() {
                return !channel.messages.empty();
            });
            
            int value = channel.messages.front();
            channel.messages.pop();
            std::cout << "Received: " << value << std::endl;
        });
        
        rt.run();
    });
    
    producer.join();
    consumer.join();
    
    return 0;
}
```