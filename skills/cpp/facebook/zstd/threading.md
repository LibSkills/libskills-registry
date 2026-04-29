# Threading

**Thread safety guarantees**

```cpp
// Zstd contexts are NOT thread-safe
// Each thread must have its own context
ZSTD_CCtx* thread1_ctx = ZSTD_createCCtx();
ZSTD_CCtx* thread2_ctx = ZSTD_createCCtx();

// Thread 1
std::thread t1([&]() {
    std::vector<char> out(ZSTD_compressBound(100));
    ZSTD_compress2(thread1_ctx, out.data(), out.size(), data1.data(), data1.size());
});

// Thread 2
std::thread t2([&]() {
    std::vector<char> out(ZSTD_compressBound(100));
    ZSTD_compress2(thread2_ctx, out.data(), out.size(), data2.data(), data2.size());
});

t1.join();
t2.join();
ZSTD_freeCCtx(thread1_ctx);
ZSTD_freeCCtx(thread2_ctx);
```

**Thread pool for parallel compression**

```cpp
class ThreadPool {
    std::vector<std::thread> workers;
    std::queue<std::function<void()>> tasks;
    std::mutex mutex;
    std::condition_variable cv;
    bool stop = false;
    
public:
    ThreadPool(size_t threads) {
        for (size_t i = 0; i < threads; ++i) {
            workers.emplace_back([this] {
                while (true) {
                    std::function<void()> task;
                    {
                        std::unique_lock<std::mutex> lock(mutex);
                        cv.wait(lock, [this] { return stop || !tasks.empty(); });
                        if (stop && tasks.empty()) return;
                        task = std::move(tasks.front());
                        tasks.pop();
                    }
                    task();
                }
            });
        }
    }
    
    void enqueue(std::function<void()> task) {
        {
            std::lock_guard<std::mutex> lock(mutex);
            tasks.push(std::move(task));
        }
        cv.notify_one();
    }
    
    ~ThreadPool() {
        {
            std::lock_guard<std::mutex> lock(mutex);
            stop = true;
        }
        cv.notify_all();
        for (auto& worker : workers) worker.join();
    }
};

// Usage: Each thread gets its own context
void parallel_compress(const std::vector<std::string>& chunks) {
    ThreadPool pool(4);
    std::vector<std::vector<char>> results(chunks.size());
    
    for (size_t i = 0; i < chunks.size(); ++i) {
        pool.enqueue([i, &chunks, &results] {
            ZSTD_CCtx* ctx = ZSTD_createCCtx();
            ZSTD_CCtx_setParameter(ctx, ZSTD_c_compressionLevel, 3);
            
            size_t max_size = ZSTD_compressBound(chunks[i].size());
            results[i].resize(max_size);
            
            size_t actual = ZSTD_compress2(ctx, results[i].data(), results[i].size(),
                                           chunks[i].data(), chunks[i].size());
            if (!ZSTD_isError(actual)) results[i].resize(actual);
            
            ZSTD_freeCCtx(ctx);
        });
    }
}
```

**Built-in multi-threading for large files**

```cpp
// Zstd can use multiple threads internally for compression
ZSTD_CCtx* cctx = ZSTD_createCCtx();
ZSTD_CCtx_setParameter(cctx, ZSTD_c_nbWorkers, 4); // Use 4 threads
ZSTD_CCtx_setParameter(cctx, ZSTD_c_compressionLevel, 3);

// This is safe to call from a single thread
// The internal threading is handled by Zstd
std::vector<char> out(ZSTD_compressBound(input.size()));
ZSTD_compress2(cctx, out.data(), out.size(), input.data(), input.size());

// Note: Decompression is always single-threaded
// For parallel decompression, split compressed frames manually
```

**Thread-safe dictionary loading**

```cpp
// Dictionaries can be shared across threads (read-only)
std::vector<char> shared_dict = load_dictionary("my_dict.zstd");

// Each thread loads the dictionary into its own context
void thread_function(const std::string& data) {
    ZSTD_CCtx* cctx = ZSTD_createCCtx();
    ZSTD_CCtx_loadDictionary(cctx, shared_dict.data(), shared_dict.size());
    // Use cctx...
    ZSTD_freeCCtx(cctx);
}
```