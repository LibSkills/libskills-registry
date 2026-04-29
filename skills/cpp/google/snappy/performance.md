# Performance

```cpp
#include <snappy.h>
#include <string>
#include <vector>
#include <chrono>
#include <iostream>

// Performance characteristics:
// - Compression speed: ~250-500 MB/s (modern CPU)
// - Decompression speed: ~500-1000 MB/s
// - Compression ratio: typically 2:1 to 5:1 for text
// - Memory overhead: minimal (no internal allocations)

// Example 1: Benchmarking compression performance
void benchmark_compression(const std::string& data, int iterations = 1000) {
    std::string compressed;
    compressed.resize(snappy::MaxCompressedLength(data.size()));
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < iterations; ++i) {
        size_t compressed_size;
        snappy::RawCompress(data.data(), data.size(),
                           compressed.data(), &compressed_size);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    double throughput = (data.size() * iterations) / (duration.count() / 1000.0) / (1024 * 1024);
    std::cout << "Compression throughput: " << throughput << " MB/s" << std::endl;
}

// Example 2: Optimal allocation patterns
class OptimizedCompressor {
public:
    // BAD: Multiple allocations
    static std::string compress_bad(const std::string& input) {
        std::string compressed;
        snappy::Compress(input.data(), input.size(), &compressed);  // Internal allocation
        return compressed;
    }
    
    // GOOD: Pre-allocate and reuse buffer
    static size_t compress_good(const std::string& input, 
                                std::vector<char>& buffer) {
        size_t needed = snappy::MaxCompressedLength(input.size());
        if (buffer.size() < needed) {
            buffer.resize(needed);
        }
        
        size_t compressed_size;
        snappy::RawCompress(input.data(), input.size(),
                           buffer.data(), &compressed_size);
        return compressed_size;
    }
};

// Example 3: Batch processing for better cache utilization
void batch_compress(const std::vector<std::string>& inputs,
                    std::vector<std::string>& outputs) {
    outputs.resize(inputs.size());
    
    // Pre-allocate all output buffers
    std::vector<std::string> temp_buffers(inputs.size());
    for (size_t i = 0; i < inputs.size(); ++i) {
        temp_buffers[i].resize(snappy::MaxCompressedLength(inputs[i].size()));
    }
    
    // Compress all items
    for (size_t i = 0; i < inputs.size(); ++i) {
        size_t compressed_size;
        snappy::RawCompress(inputs[i].data(), inputs[i].size(),
                           temp_buffers[i].data(), &compressed_size);
        temp_buffers[i].resize(compressed_size);
    }
    
    outputs = std::move(temp_buffers);
}

// Example 4: Memory alignment considerations
// BAD: Unaligned data access
void compress_unaligned(const char* data, size_t size) {
    std::string compressed;
    snappy::Compress(data, size, &compressed);
}

// GOOD: Aligned buffer (may improve performance on some architectures)
void compress_aligned(const char* data, size_t size) {
    alignas(64) std::vector<char> aligned_data(data, data + size);
    std::string compressed;
    compressed.resize(snappy::MaxCompressedLength(size));
    
    size_t compressed_size;
    snappy::RawCompress(aligned_data.data(), size,
                       compressed.data(), &compressed_size);
    compressed.resize(compressed_size);
}

// Example 5: Avoiding unnecessary copies
class ZeroCopyCompressor {
public:
    // BAD: Multiple string copies
    static std::string compress_with_copies(const std::string& input) {
        std::string temp = input;  // Copy 1
        std::string compressed;
        snappy::Compress(temp.data(), temp.size(), &compressed);  // Copy 2
        return compressed;
    }
    
    // GOOD: Direct compression without intermediate copies
    static std::string compress_direct(const std::string& input) {
        std::string compressed;
        compressed.resize(snappy::MaxCompressedLength(input.size()));
        
        size_t compressed_size;
        snappy::RawCompress(input.data(), input.size(),
                           compressed.data(), &compressed_size);
        compressed.resize(compressed_size);
        return compressed;
    }
};

// Example 6: SIMD-friendly data layout
// Snappy internally uses SIMD instructions for better performance
// Ensure your data is contiguous for optimal SIMD utilization
struct ContiguousData {
    std::vector<char> data;
    size_t size;
    
    // BAD: Non-contiguous data
    static ContiguousData from_vector_of_strings(const std::vector<std::string>& strings) {
        ContiguousData result;
        for (const auto& s : strings) {
            result.data.insert(result.data.end(), s.begin(), s.end());
        }
        result.size = result.data.size();
        return result;
    }
    
    // GOOD: Pre-allocate contiguous buffer
    static ContiguousData from_vector_of_strings_optimized(const std::vector<std::string>& strings) {
        size_t total_size = 0;
        for (const auto& s : strings) {
            total_size += s.size();
        }
        
        ContiguousData result;
        result.data.reserve(total_size);
        for (const auto& s : strings) {
            result.data.insert(result.data.end(), s.begin(), s.end());
        }
        result.size = total_size;
        return result;
    }
};
```