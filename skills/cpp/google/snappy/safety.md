# Safety

```cpp
// RED LINE 1: NEVER pass invalid compressed data to Uncompress
// BAD: Uncompressing random data
std::string random_data = get_random_bytes(1000);
std::string result;
snappy::Uncompress(random_data.data(), random_data.size(), &result);  // CRASH!

// GOOD: Always validate first
std::string compressed = get_compressed_data();
if (!snappy::IsValidCompressedBuffer(compressed.data(), compressed.size())) {
    throw std::invalid_argument("Invalid compressed data");
}
std::string result;
snappy::Uncompress(compressed.data(), compressed.size(), &result);

// RED LINE 2: NEVER assume compressed size is smaller than original
// BAD: Buffer overflow risk
char input[100] = "incompressible data that might expand";
char output[50];  // Too small!
size_t output_size;
snappy::RawCompress(input, 100, output, &output_size);  // Buffer overflow!

// GOOD: Always use MaxCompressedLength
char input[100] = "incompressible data that might expand";
std::vector<char> output(snappy::MaxCompressedLength(100));
size_t output_size;
snappy::RawCompress(input, 100, output.data(), &output_size);

// RED LINE 3: NEVER use Uncompress without checking return value
// BAD: Ignoring failure
std::string result;
snappy::Uncompress(data, size, &result);  // result may be incomplete

// GOOD: Always check
std::string result;
if (!snappy::Uncompress(data, size, &result)) {
    // Handle error - data was corrupted or invalid
    throw std::runtime_error("Decompression failed");
}

// RED LINE 4: NEVER pass overlapping input/output buffers
// BAD: Same buffer for input and output
char buffer[1000];
snappy::RawCompress(buffer, 100, buffer, &size);  // Undefined behavior!

// GOOD: Use separate buffers
char input[1000];
char output[snappy::MaxCompressedLength(1000)];
size_t size;
snappy::RawCompress(input, 100, output, &size);

// RED LINE 5: NEVER trust GetUncompressedLength for untrusted data
// BAD: Allocating based on untrusted length
size_t uncompressed_size;
snappy::GetUncompressedLength(compressed.data(), compressed.size(), &uncompressed_size);
std::vector<char> result(uncompressed_size);  // May allocate huge memory!

// GOOD: Validate and limit allocation
size_t uncompressed_size;
if (!snappy::GetUncompressedLength(compressed.data(), compressed.size(), &uncompressed_size)) {
    throw std::runtime_error("Invalid compressed data");
}
if (uncompressed_size > MAX_ALLOWED_SIZE) {
    throw std::runtime_error("Decompressed size exceeds limit");
}
std::vector<char> result(uncompressed_size);
```