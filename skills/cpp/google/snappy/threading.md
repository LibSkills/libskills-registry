# Threading

```cpp
#include <snappy.h>
#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <atomic>
#include <iostream>

// Thread Safety Guarantees:
// - All snappy functions are thread-safe for independent operations
// - No global state is modified
// - No internal synchronization is needed
// - Input and output buffers must not be shared between threads

// Example 1: Thread-safe compression (no shared state)
void thread_safe_compression() {
    const std::string data = "Thread-safe compression test data";
    
    std::vector<std::thread> threads;
    std::vector<std::string> results(4);
    
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&data, &result = results[i]]() {
            std::string compressed;
            compressed.resize(snappy::MaxCompressedLength(data.size()));
            
            size_t compressed_size;
            snappy::RawCompress(data.data(), data.size(),
                               compressed.data(), &compressed_size);
            compressed.resize(compressed_size);
            result = std::move(compressed);
        });
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    // All results should be identical
    for (size_t i = 1; i < results.size(); ++i) {
        if (results[i] != results[0]) {
            std::cerr << "Thread safety violation!" << std::endl;
        }
    }
}

// Example 2: Thread-safe buffer pool with mutex
class ThreadSafeBufferPool {
    struct Buffer {
        std::vector<char> data;
        bool in_use = false;
    };
    
    std::vector<Buffer> buffers_;
    size_t buffer_size_;
    std::mutex mutex_;
    
public:
    explicit ThreadSafeBufferPool(size_t max_input_size, size_t pool_size = 10)
        : buffer_size_(snappy::MaxCompressedLength(max_input_size))
        , buffers_(pool_size) {
        for (auto& buf : buffers_) {
            buf.data.resize(buffer_size_);
        }
    }
    
    class BufferHandle {
        ThreadSafeBufferPool& pool_;
        size_t index_;
        bool released_ = false;
        
    public:
        BufferHandle(ThreadSafeBufferPool& pool, size_t index)
            : pool_(pool), index_(index) {}
        
        ~BufferHandle() {
            if (!released_) {
                std::lock_guard<std::mutex> lock(pool_.mutex_);
                pool_.buffers_[index_].in_use = false;
            }
        }
        
        BufferHandle(BufferHandle&& other) noexcept
            : pool_(other.pool_), index_(other.index_), released_(other.released_) {
            other.released_ = true;
        }
        
        BufferHandle& operator=(BufferHandle&& other) noexcept {
            if (this != &other) {
                if (!released_) {
                    std::lock_guard<std::mutex> lock(pool_.mutex_);
                    pool_.buffers_[index_].in_use = false;
                }
                pool_ = other.pool_;
                index_ = other.index_;
                released_ = other.released_;
                other.released_ = true;
            }
            return *this;
        }
        
        char* data() { return pool_.buffers_[index_].data.data(); }
        size_t capacity() const { return pool_.buffer_size_; }
    };
    
    BufferHandle acquire() {
        std::lock_guard<std::mutex> lock(mutex_);
        for (size_t i = 0; i < buffers_.size(); ++i) {
            if (!buffers_[i].in_use) {
                buffers_[i].in_use = true;
                return BufferHandle(*this, i);
            }
        }
        throw std::runtime_error("No available buffers");
    }
};

// Example 3: Parallel compression of large data
class ParallelCompressor {
    static constexpr size_t CHUNK_SIZE = 1024 * 1024;  // 1MB chunks
    
public:
    struct CompressedChunk {
        std::string data;
        size_t original_size;
    };
    
    static std::vector<CompressedChunk> compress_parallel(const std::string& input) {
        size_t num_chunks = (input.size() + CHUNK_SIZE - 1) / CHUNK_SIZE;
        std::vector<CompressedChunk> results(num_chunks);
        
        std::vector<std::thread> threads;
        threads.reserve(num_chunks);
        
        for (size_t i = 0; i < num_chunks; ++i) {
            threads.emplace_back([&input, &results, i, num_chunks]() {
                size_t start = i * CHUNK_SIZE;
                size_t end = std::min(start + CHUNK_SIZE, input.size());
                size_t chunk_size = end - start;
                
                std::string compressed;
                compressed.resize(snappy::MaxCompressedLength(chunk_size));
                
                size_t compressed_size;
                snappy::RawCompress(input.data() + start, chunk_size,
                                   compressed.data(), &compressed_size);
                compressed.resize(compressed_size);
                
                results[i].data = std::move(compressed);
                results[i].original_size = chunk_size;
            });
        }
        
        for (auto& t : threads) {
            t.join();
        }
        
        return results;
    }
    
    static std::string decompress_parallel(const std::vector<CompressedChunk>& chunks) {
        // Calculate total size
        size_t total_size = 0;
        for (const auto& chunk : chunks) {
            total_size += chunk.original_size;
        }
        
        std::string result(total_size, '\0');
        std::vector<std::thread> threads;
        threads.reserve(chunks.size());
        
        size_t offset = 0;
        for (const auto& chunk : chunks) {
            size_t current_offset = offset;
            threads.emplace_back([&result, &chunk, current_offset]() {
                snappy::RawUncompress(chunk.data.data(), chunk.data.size(),
                                     result.data() + current_offset);
            });
            offset += chunk.original_size;
        }
        
        for (auto& t : threads) {
            t.join();
        }
        
        return result;
    }
};

// Example 4: Thread-safe wrapper with atomic operations
class AtomicCompressor {
    std::atomic<size_t> total_compressed_bytes_{0};
    std::atomic<size_t> total_original_bytes_{0};
    
public:
    std::string compress(const std::string& input) {
        std::string compressed;
        compressed.resize(snappy::MaxCompressedLength(input.size()));
        
        size_t compressed_size;
        snappy::RawCompress(input.data(), input.size(),
                           compressed.data(), &compressed_size);
        compressed.resize(compressed_size);
        
        // Thread-safe statistics update
        total_compressed_bytes_.fetch_add(compressed_size, std::memory_order_relaxed);
        total_original_bytes_.fetch_add(input.size(), std::memory_order_relaxed);
        
        return compressed;
    }
    
    double compression_ratio() const {
        size_t compressed = total_compressed_bytes_.load(std::memory_order_relaxed);
        size_t original = total_original_bytes_.load(std::memory_order_relaxed);
        return original > 0 ? static_cast<double>(compressed) / original : 0.0;
    }
};

// Example 5: Thread-local buffer for maximum performance
class ThreadLocalCompressor {
    static thread_local std::vector<char> buffer_;
    
public:
    static std::string compress(const std::string& input) {
        size_t needed = snappy::MaxCompressedLength(input.size());
        if (buffer_.size() < needed) {
            buffer_.resize(needed);
        }
        
        size_t compressed_size;
        snappy::RawCompress(input.data(), input.size(),
                           buffer_.data(), &compressed_size);
        
        return std::string(buffer_.data(), compressed_size);
    }
    
    static std::string decompress(const std::string& input) {
        size_t uncompressed_size;
        if (!snappy::GetUncompressedLength(input.data(), input.size(),
                                           &uncompressed_size)) {
            throw std::runtime_error("Invalid compressed data");
        }
        
        if (buffer_.size() < uncompressed_size) {
            buffer_.resize(uncompressed_size);
        }
        
        if (!snappy::RawUncompress(input.data(), input.size(),
                                   buffer_.data())) {
            throw std::runtime_error("Decompression failed");
        }
        
        return std::string(buffer_.data(), uncompressed_size);
    }
};

thread_local std::vector<char> ThreadLocalCompressor::buffer_;
```