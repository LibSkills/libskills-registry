# Pitfalls

```cpp
// PITFALL 1: Not checking Uncompress return value
// BAD: Ignoring return value
std::string compressed = get_compressed_data();
std::string uncompressed;
snappy::Uncompress(compressed.data(), compressed.size(), &uncompressed);  // May silently fail

// GOOD: Always check return value
std::string compressed = get_compressed_data();
std::string uncompressed;
if (!snappy::Uncompress(compressed.data(), compressed.size(), &uncompressed)) {
    throw std::runtime_error("Failed to decompress data");
}

// PITFALL 2: Using wrong size type for compressed data
// BAD: Using int instead of size_t
int compressed_size = compressed.length();  // May overflow for large data

// GOOD: Use size_t consistently
size_t compressed_size = compressed.size();

// PITFALL 3: Not pre-allocating enough space for compression
// BAD: Assuming compressed size is smaller
std::string compressed;
compressed.resize(input.size());  // May be too small!

// GOOD: Use MaxCompressedLength
std::string compressed;
compressed.resize(snappy::MaxCompressedLength(input.size()));

// PITFALL 4: Passing null pointers
// BAD: Null input
snappy::Compress(nullptr, 0, &output);  // Undefined behavior

// GOOD: Check for null
if (input == nullptr || input_size == 0) {
    output.clear();
    return;
}
snappy::Compress(input, input_size, &output);

// PITFALL 5: Using compressed data after source is modified
// BAD: Source data changes
std::string source = "original data";
std::string compressed;
snappy::Compress(source.data(), source.size(), &compressed);
source = "modified";  // compressed still references old data? No, it's a copy

// GOOD: Understand that compressed data is independent
std::string source = "original data";
std::string compressed;
snappy::Compress(source.data(), source.size(), &compressed);
// compressed is now a standalone copy

// PITFALL 6: Not handling incompressible data
// BAD: Assuming compression always reduces size
std::string compressed;
snappy::Compress(input.data(), input.size(), &compressed);
if (compressed.size() >= input.size()) {
    // Store original instead
    store_original(input);
} else {
    store_compressed(compressed);
}

// GOOD: Check if compression was beneficial
std::string compressed;
snappy::Compress(input.data(), input.size(), &compressed);
if (compressed.size() < input.size()) {
    store_compressed(compressed);
} else {
    store_original(input);
}

// PITFALL 7: Mixing RawCompress and Uncompress
// BAD: Using RawCompress with string Uncompress
char* compressed = new char[snappy::MaxCompressedLength(input_size)];
size_t compressed_size;
snappy::RawCompress(input, input_size, compressed, &compressed_size);
std::string uncompressed;
snappy::Uncompress(compressed, compressed_size, &uncompressed);  // Works but inconsistent

// GOOD: Use matching API pairs
std::string compressed;
snappy::Compress(input, input_size, &compressed);
std::string uncompressed;
snappy::Uncompress(compressed.data(), compressed.size(), &uncompressed);
```