# Best Practices

```cpp
// 1. Use RAII wrappers for handle lifecycle management
#include <uv.h>
#include <memory>

struct UvHandleDeleter {
    void operator()(uv_handle_t* h) const {
        if (h && !uv_is_closing(h)) {
            uv_close(h, [](uv_handle_t* handle) {
                delete handle;
            });
        }
    }
};

using UvTimerPtr = std::unique_ptr<uv_timer_t, UvHandleDeleter>;

UvTimerPtr make_timer(uv_loop_t* loop, uv_timer_cb cb, uint64_t timeout, uint64_t repeat) {
    auto timer = UvTimerPtr(new uv_timer_t);
    uv_timer_init(loop, timer.get());
    uv_timer_start(timer.get(), cb, timeout, repeat);
    return timer;
}
```

```cpp
// 2. Centralized error handling pattern
#include <uv.h>
#include <iostream>
#include <stdexcept>

class UvError : public std::runtime_error {
public:
    explicit UvError(int err) 
        : std::runtime_error(uv_strerror(err)), code_(err) {}
    int code() const { return code_; }
private:
    int code_;
};

#define UV_CHECK(expr) do { \
    int r = (expr); \
    if (r < 0) throw UvError(r); \
} while(0)

void safe_bind(uv_tcp_t* server, const struct sockaddr* addr) {
    UV_CHECK(uv_tcp_bind(server, addr, 0));
}
```

```cpp
// 3. Thread pool configuration for blocking operations
#include <uv.h>
#include <iostream>

int main() {
    // Configure thread pool size before any async operations
    char env[] = "UV_THREADPOOL_SIZE=8";
    putenv(env);
    
    // Or use uv_os_setenv
    uv_os_setenv("UV_THREADPOOL_SIZE", "8");
    
    // Now proceed with async operations
    uv_loop_t *loop = uv_default_loop();
    uv_fs_t req;
    uv_fs_open(loop, &req, "file.txt", O_RDONLY, 0, [](uv_fs_t* req) {
        if (req->result >= 0) {
            std::cout << "File opened successfully" << std::endl;
        }
        uv_fs_req_cleanup(req);
    });
    
    uv_run(loop, UV_RUN_DEFAULT);
    return 0;
}
```

```cpp
// 4. Proper shutdown sequence
#include <uv.h>
#include <vector>

class Server {
public:
    void shutdown() {
        uv_stop(loop_);
        // Close all handles
        for (auto& h : handles_) {
            if (!uv_is_closing(h)) {
                uv_close(h, [](uv_handle_t* handle) {
                    // Handle cleanup
                });
            }
        }
        // Run loop one more time to process close callbacks
        uv_run(loop_, UV_RUN_NOWAIT);
        uv_loop_close(loop_);
    }
    
private:
    uv_loop_t* loop_;
    std::vector<uv_handle_t*> handles_;
};
```

```cpp
// 5. Buffer management for network I/O
#include <uv.h>
#include <vector>
#include <memory>

class BufferPool {
public:
    uv_buf_t get_buffer() {
        if (pool_.empty()) {
            return uv_buf_init(new char[4096], 4096);
        }
        auto buf = pool_.back();
        pool_.pop_back();
        return buf;
    }
    
    void return_buffer(uv_buf_t buf) {
        pool_.push_back(buf);
    }
    
    ~BufferPool() {
        for (auto& buf : pool_) {
            delete[] buf.base;
        }
    }
    
private:
    std::vector<uv_buf_t> pool_;
};
```