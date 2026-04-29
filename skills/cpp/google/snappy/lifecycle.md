# Lifecycle

```cpp
#include <snappy.h>
#include <string>
#include <vector>
#include <memory>
#include <cstring>

// Construction: Snappy is stateless - no objects to construct
// All functions are free functions in the snappy namespace

// Resource Management: Snappy doesn't manage resources internally
// All memory management is the caller's responsibility

// Example 1: Proper buffer lifecycle
class CompressionBuffer {
    std::vector<char> buffer_;
    size_t capacity_;
    
public:
    explicit CompressionBuffer(size_t max_input_size) 
        : buffer_(snappy::MaxCompressedLength(max_input_size))
        , capacity_(max_input_size) {}
    
    // Move constructor
    CompressionBuffer(CompressionBuffer&& other) noexcept
        : buffer_(std::move(other.buffer_))
        , capacity_(other.capacity_) {
        other.capacity_ = 0;
    }
    
    // Move assignment
    CompressionBuffer& operator=(CompressionBuffer&& other) noexcept {
        if (this != &other) {
            buffer_ = std::move(other.buffer_);
            capacity_ = other.capacity_;
            other.capacity_ = 0;
        }
        return *this;
    }
    
    // Copy operations (expensive - use with caution)
    CompressionBuffer(const CompressionBuffer& other)
        : buffer_(other.buffer_)
        , capacity_(other.capacity_) {}
    
    CompressionBuffer& operator=(const CompressionBuffer& other) {
        if (this != &other) {
            buffer_ = other.buffer_;
            capacity_ = other.capacity_;
        }
        return *this;
    }
    
    ~CompressionBuffer() = default;
    
    size_t compress(const char* input, size_t input_size) {
        if (input_size > capacity_) {
            throw std::length_error("Input exceeds buffer capacity");
        }
        
        size_t compressed_size;
        snappy::RawCompress(input, input_size, buffer_.data(), &compressed_size);
        return compressed_size;
    }
    
    const char* data() const { return buffer_.data(); }
    size_t capacity() const { return capacity_; }
};

// Example 2: String-based lifecycle (simpler, but involves allocations)
class CompressedString {
    std::string compressed_data_;
    bool is_valid_ = false;
    
public:
    CompressedString() = default;
    
    explicit CompressedString(const std::string& input) {
        compress(input);
    }
    
    // Move constructor
    CompressedString(CompressedString&& other) noexcept
        : compressed_data_(std::move(other.compressed_data_))
        , is_valid_(other.is_valid_) {
        other.is_valid_ = false;
    }
    
    // Move assignment
    CompressedString& operator=(CompressedString&& other) noexcept {
        if (this != &other) {
            compressed_data_ = std::move(other.compressed_data_);
            is_valid_ = other.is_valid_;
            other.is_valid_ = false;
        }
        return *this;
    }
    
    // Copy constructor
    CompressedString(const CompressedString& other)
        : compressed_data_(other.compressed_data_)
        , is_valid_(other.is_valid_) {}
    
    // Copy assignment
    CompressedString& operator=(const CompressedString& other) {
        if (this != &other) {
            compressed_data_ = other.compressed_data_;
            is_valid_ = other.is_valid_;
        }
        return *this;
    }
    
    ~CompressedString() = default;
    
    void compress(const std::string& input) {
        compressed_data_.clear();
        compressed_data_.resize(snappy::MaxCompressedLength(input.size()));
        
        size_t compressed_size;
        snappy::RawCompress(input.data(), input.size(),
                           compressed_data_.data(), &compressed_size);
        compressed_data_.resize(compressed_size);
        is_valid_ = true;
    }
    
    std::string decompress() const {
        if (!is_valid_) {
            throw std::runtime_error("No compressed data available");
        }
        
        size_t uncompressed_size;
        if (!snappy::GetUncompressedLength(compressed_data_.data(),
                                           compressed_data_.size(),
                                           &uncompressed_size)) {
            throw std::runtime_error("Invalid compressed data");
        }
        
        std::string result;
        result.resize(uncompressed_size);
        
        if (!snappy::RawUncompress(compressed_data_.data(),
                                   compressed_data_.size(),
                                   result.data())) {
            throw std::runtime_error("Decompression failed");
        }
        
        return result;
    }
    
    bool is_valid() const { return is_valid_; }
    const std::string& data() const { return compressed_data_; }
};

// Example 3: Pooled buffer management (for high-performance scenarios)
class BufferPool {
    struct Buffer {
        std::vector<char> data;
        bool in_use = false;
    };
    
    std::vector<Buffer> buffers_;
    size_t buffer_size_;
    
public:
    explicit BufferPool(size_t max_input_size, size_t pool_size = 10)
        : buffer_size_(snappy::MaxCompressedLength(max_input_size))
        , buffers_(pool_size) {
        for (auto& buf : buffers_) {
            buf.data.resize(buffer_size_);
        }
    }
    
    ~BufferPool() = default;
    
    // Non-copyable, non-movable (pool has unique ownership)
    BufferPool(const BufferPool&) = delete;
    BufferPool& operator=(const BufferPool&) = delete;
    BufferPool(BufferPool&&) = delete;
    BufferPool& operator=(BufferPool&&) = delete;
    
    class BufferHandle {
        BufferPool& pool_;
        size_t index_;
        bool released_ = false;
        
    public:
        BufferHandle(BufferPool& pool, size_t index)
            : pool_(pool), index_(index) {}
        
        ~BufferHandle() {
            if (!released_) {
                pool_.buffers_[index_].in_use = false;
            }
        }
        
        // Move-only
        BufferHandle(BufferHandle&& other) noexcept
            : pool_(other.pool_), index_(other.index_), released_(other.released_) {
            other.released_ = true;
        }
        
        BufferHandle& operator=(BufferHandle&& other) noexcept {
            if (this != &other) {
                if (!released_) {
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
        
        void release() {
            if (!released_) {
                pool_.buffers_[index_].in_use = false;
                released_ = true;
            }
        }
    };
    
    BufferHandle acquire() {
        for (size_t i = 0; i < buffers_.size(); ++i) {
            if (!buffers_[i].in_use) {
                buffers_[i].in_use = true;
                return BufferHandle(*this, i);
            }
        }
        throw std::runtime_error("No available buffers in pool");
    }
};
```