# Lifecycle

```cpp
// Construction: Initialize loop and handles
#include <uv.h>

int main() {
    // Create a new loop (not default)
    uv_loop_t *loop = new uv_loop_t;
    uv_loop_init(loop);
    
    // Initialize handles
    uv_tcp_t *server = new uv_tcp_t;
    uv_tcp_init(loop, server);
    
    // Initialize timer
    uv_timer_t *timer = new uv_timer_t;
    uv_timer_init(loop, timer);
    
    // Run the loop
    uv_run(loop, UV_RUN_DEFAULT);
    
    // Cleanup
    uv_loop_close(loop);
    delete loop;
    return 0;
}
```

```cpp
// Destruction: Proper cleanup sequence
#include <uv.h>
#include <vector>

void cleanup_handles(std::vector<uv_handle_t*>& handles) {
    // Step 1: Stop all active handles
    for (auto* h : handles) {
        if (uv_is_active(h)) {
            uv_handle_t type = h->type;
            switch (type) {
                case UV_TIMER:
                    uv_timer_stop((uv_timer_t*)h);
                    break;
                case UV_TCP:
                    uv_read_stop((uv_stream_t*)h);
                    break;
                default:
                    break;
            }
        }
    }
    
    // Step 2: Close all handles
    for (auto* h : handles) {
        if (!uv_is_closing(h)) {
            uv_close(h, [](uv_handle_t* handle) {
                delete handle;
            });
        }
    }
    
    // Step 3: Run loop to process close callbacks
    uv_run(uv_default_loop(), UV_RUN_NOWAIT);
}
```

```cpp
// Resource management: Handle pools and reuse
#include <uv.h>
#include <vector>

class HandlePool {
public:
    uv_tcp_t* acquire() {
        if (pool_.empty()) {
            uv_tcp_t* tcp = new uv_tcp_t;
            uv_tcp_init(loop_, tcp);
            return tcp;
        }
        auto* tcp = pool_.back();
        pool_.pop_back();
        // Reset handle state
        uv_tcp_init(loop_, tcp);
        return tcp;
    }
    
    void release(uv_tcp_t* tcp) {
        uv_close((uv_handle_t*)tcp, [](uv_handle_t* handle) {
            // Don't delete, just return to pool
        });
        pool_.push_back(tcp);
    }
    
    ~HandlePool() {
        for (auto* tcp : pool_) {
            uv_close((uv_handle_t*)tcp, [](uv_handle_t* handle) {
                delete handle;
            });
        }
    }
    
private:
    uv_loop_t* loop_;
    std::vector<uv_tcp_t*> pool_;
};
```

```cpp
// Move semantics: Not directly supported, use pointers
#include <uv.h>
#include <memory>

// libuv handles are not movable, use pointers and smart pointers
struct UvLoopDeleter {
    void operator()(uv_loop_t* loop) const {
        if (loop) {
            uv_loop_close(loop);
            delete loop;
        }
    }
};

using UvLoopPtr = std::unique_ptr<uv_loop_t, UvLoopDeleter>;

class Server {
public:
    Server() : loop_(new uv_loop_t) {
        uv_loop_init(loop_.get());
    }
    
    // Move constructor
    Server(Server&& other) noexcept : loop_(std::move(other.loop_)) {}
    
    // Move assignment
    Server& operator=(Server&& other) noexcept {
        if (this != &other) {
            loop_ = std::move(other.loop_);
        }
        return *this;
    }
    
private:
    UvLoopPtr loop_;
};
```