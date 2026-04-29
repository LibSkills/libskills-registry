# Quickstart

```cpp
#include <snappy.h>
#include <string>
#include <vector>
#include <cassert>
#include <iostream>

// Pattern 1: Compress a string
void compress_string() {
    std::string input = "Hello, World! This is a test string for Snappy compression.";
    std::string compressed;
    
    snappy::Compress(input.data(), input.size(), &compressed);
    std::cout << "Original size: " << input.size() << ", Compressed size: " << compressed.size() << std::endl;
}

// Pattern 2: Uncompress a string
void uncompress_string() {
    std::string original = "Data to compress and decompress";
    std::string compressed;
    std::string uncompressed;
    
    snappy::Compress(original.data(), original.size(), &compressed);
    
    if (snappy::Uncompress(compressed.data(), compressed.size(), &uncompressed)) {
        assert(original == uncompressed);
        std::cout << "Successfully uncompressed!" << std::endl;
    }
}

// Pattern 3: Check if data is Snappy compressed
void check_compressed() {
    std::string data = "Some data";
    std::string compressed;
    snappy::Compress(data.data(), data.size(), &compressed);
    
    bool is_compressed = snappy::IsValidCompressedBuffer(compressed.data(), compressed.size());
    std::cout << "Is valid compressed data: " << (is_compressed ? "yes" : "no") << std::endl;
}

// Pattern 4: Get uncompressed length
void get_uncompressed_length() {
    std::string original = "Test data for length checking";
    std::string compressed;
    snappy::Compress(original.data(), original.size(), &compressed);
    
    size_t uncompressed_length;
    if (snappy::GetUncompressedLength(compressed.data(), compressed.size(), &uncompressed_length)) {
        assert(uncompressed_length == original.size());
        std::cout << "Uncompressed length: " << uncompressed_length << std::endl;
    }
}

// Pattern 5: Compress with raw array (char*)
void compress_raw_array() {
    const char* input = "Raw array compression test";
    size_t input_size = strlen(input);
    
    // Pre-allocate maximum possible compressed size
    size_t max_compressed_size = snappy::MaxCompressedLength(input_size);
    std::vector<char> compressed(max_compressed_size);
    
    size_t compressed_size;
    snappy::RawCompress(input, input_size, compressed.data(), &compressed_size);
    compressed.resize(compressed_size);
    
    std::cout << "Compressed " << input_size << " bytes to " << compressed_size << " bytes" << std::endl;
}

// Pattern 6: Uncompress to raw array
void uncompress_raw_array() {
    std::string original = "Raw array decompression";
    std::string compressed;
    snappy::Compress(original.data(), original.size(), &compressed);
    
    size_t uncompressed_length;
    snappy::GetUncompressedLength(compressed.data(), compressed.size(), &uncompressed_length);
    
    std::vector<char> uncompressed(uncompressed_length);
    if (snappy::RawUncompress(compressed.data(), compressed.size(), uncompressed.data())) {
        assert(std::string(uncompressed.data(), uncompressed.size()) == original);
        std::cout << "Raw uncompress successful!" << std::endl;
    }
}

// Pattern 7: Compress vector of bytes
void compress_byte_vector() {
    std::vector<uint8_t> data = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    std::string compressed;
    
    snappy::Compress(reinterpret_cast<const char*>(data.data()), data.size(), &compressed);
    std::cout << "Compressed vector of " << data.size() << " bytes" << std::endl;
}

// Pattern 8: Check compression ratio
void check_compression_ratio() {
    std::string input = "AAAAABBBBBCCCCCDDDDDEEEEE";  // Repetitive data compresses well
    std::string compressed;
    
    snappy::Compress(input.data(), input.size(), &compressed);
    
    double ratio = static_cast<double>(compressed.size()) / input.size();
    std::cout << "Compression ratio: " << ratio << " (smaller is better)" << std::endl;
}
```