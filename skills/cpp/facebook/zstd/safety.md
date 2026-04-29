# Safety

**Red Line 1: Never pass null pointers to Zstd functions**

BAD:
```cpp
ZSTD_CCtx* cctx = nullptr;
ZSTD_compress2(cctx, nullptr, 0, nullptr, 0); // Undefined behavior
```

GOOD:
```cpp
ZSTD_CCtx* cctx = ZSTD_createCCtx();
if (!cctx) throw std::runtime_error("Failed to create context");
std::vector<char> out(ZSTD_compressBound(100));
std::string in = "test";
size_t result = ZSTD_compress2(cctx, out.data(), out.size(), in.data(), in.size());
if (ZSTD_isError(result)) throw std::runtime_error(ZSTD_getErrorName(result));
ZSTD_freeCCtx(cctx);
```

**Red Line 2: Never use compressed data without checking content size**

BAD:
```cpp
void process_compressed(const std::vector<char>& compressed) {
    std::string result(1000000, '\0'); // Assume 1MB
    ZSTD_decompress(result.data(), result.size(), compressed.data(), compressed.size());
    // Buffer overflow if original was larger
}
```

GOOD:
```cpp
void process_compressed(const std::vector<char>& compressed) {
    unsigned long long size = ZSTD_getFrameContentSize(compressed.data(), compressed.size());
    if (size == ZSTD_CONTENTSIZE_ERROR) throw std::runtime_error("Invalid data");
    if (size == ZSTD_CONTENTSIZE_UNKNOWN) {
        // Use streaming decompression
        return streaming_decompress(compressed);
    }
    std::string result(size, '\0');
    size_t actual = ZSTD_decompress(result.data(), result.size(), compressed.data(), compressed.size());
    if (ZSTD_isError(actual)) throw std::runtime_error(ZSTD_getErrorName(actual));
}
```

**Red Line 3: Never ignore ZSTD_isError return values**

BAD:
```cpp
size_t compressed_size = ZSTD_compress(out.data(), out.size(), in.data(), in.size(), 1);
// Assume success, use compressed_size directly
```

GOOD:
```cpp
size_t compressed_size = ZSTD_compress(out.data(), out.size(), in.data(), in.size(), 1);
if (ZSTD_isError(compressed_size)) {
    throw std::runtime_error(ZSTD_getErrorName(compressed_size));
}
// Safe to use compressed_size
```

**Red Line 4: Never use a context after freeing it**

BAD:
```cpp
ZSTD_CCtx* cctx = ZSTD_createCCtx();
ZSTD_freeCCtx(cctx);
ZSTD_compress2(cctx, out.data(), out.size(), in.data(), in.size()); // Use after free
```

GOOD:
```cpp
ZSTD_CCtx* cctx = ZSTD_createCCtx();
// Use cctx...
ZSTD_freeCCtx(cctx);
cctx = nullptr; // Prevent accidental reuse
```

**Red Line 5: Never pass overlapping input/output buffers**

BAD:
```cpp
std::vector<char> buffer(1000);
ZSTD_compress(buffer.data(), buffer.size(), buffer.data(), 100, 1); // Overlapping!
```

GOOD:
```cpp
std::vector<char> input(1000, 'a');
std::vector<char> output(ZSTD_compressBound(input.size()));
size_t result = ZSTD_compress(output.data(), output.size(), input.data(), input.size(), 1);
if (ZSTD_isError(result)) throw std::runtime_error(ZSTD_getErrorName(result));
```