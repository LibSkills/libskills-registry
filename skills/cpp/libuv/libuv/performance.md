# Performance

```cpp
// 1. Minimize memory allocations in hot paths
#include <uv.h>
#include <vector>

// BAD: Allocating in callback
void read_cb(uv_stream_t* stream, ssize_t nread, const uv_buf_t* buf) {
    auto* data = new std::vector<char>(buf->base, buf->base + nread);
    // Process data...
    delete data;
}

// GOOD: Pre-allocate and reuse buffers
class BufferManager {
public:
    uv_buf_t get_buffer() {
        if (free_buffers_.empty()) {
            return uv_buf_init(new char[65536], 65536);
        }
        auto buf = free_buffers_.back();
        free_buffers_.pop_back();
        return buf;
    }
    
    void return_buffer(uv_buf_t buf) {
        free_buffers_.push_back(buf);
    }
    
private:
    std::vector<uv_buf_t> free_buffers_;
};
```

```cpp
// 2. Use UV_RUN_NOWAIT for non-blocking event processing
#include <uv.h>
#include <chrono>

void high_performance_loop(uv_loop_t* loop) {
    while (true) {
        // Process events without blocking
        int result = uv_run(loop, UV_RUN_NOWAIT);
        
        if (result == 0) {
            // No pending events, yield to OS
            std::this_thread::sleep_for(std::chrono::microseconds(100));
        }
        
        // Do other work here
        process_cpu_tasks();
    }
}
```

```cpp
// 3. Configure thread pool size for optimal performance
#include <uv.h>
#include <thread>

int main() {
    // Set thread pool size based on CPU cores
    int num_cores = std::thread::hardware_concurrency();
    std::string pool_size = std::to_string(num_cores);
    uv_os_setenv("UV_THREADPOOL_SIZE", pool_size.c_str());
    
    // For I/O bound workloads, use 2x cores
    // For CPU bound workloads, use 1x cores
    uv_loop_t* loop = uv_default_loop();
    
    // Now async operations will use optimal thread pool
    uv_run(loop, UV_RUN_DEFAULT);
    return 0;
}
```

```cpp
// 4. Batch file operations to reduce overhead
#include <uv.h>
#include <vector>

// BAD: Individual file operations
void read_files_separately() {
    for (auto& filename : files) {
        uv_fs_t req;
        uv_fs_open(uv_default_loop(), &req, filename.c_str(), O_RDONLY, 0, nullptr);
        uv_fs_req_cleanup(&req);
    }
}

// GOOD: Batch operations using single request
void read_files_batched() {
    uv_fs_t req;
    // Use uv_fs_scandir or uv_fs_read with multiple buffers
    uv_fs_scandir(uv_default_loop(), &req, ".", 0, [](uv_fs_t* req) {
        // Process all files at once
        uv_dirent_t ent;
        while (uv_fs_scandir_next(req, &ent) != UV_EOF) {
            // Process each entry
        }
        uv_fs_req_cleanup(req);
    });
}
```

```cpp
// 5. Use zero-copy techniques where possible
#include <uv.h>

// BAD: Copying data unnecessarily
void process_data(uv_buf_t buf) {
    std::vector<char> copy(buf.base, buf.base + buf.len);
    // Process copy...
}

// GOOD: Work directly with buffer
void process_data_direct(uv_buf_t buf) {
    // Process buf.base directly without copying
    process_in_place(buf.base, buf.len);
}
```