# Pitfalls

**Pitfall 1: Not checking return values for errors**

BAD:
```cpp
std::vector<char> compress(const std::string& input) {
    std::vector<char> compressed(ZSTD_compressBound(input.size()));
    ZSTD_compress(compressed.data(), compressed.size(), input.data(), input.size(), 1);
    return compressed; // Might contain garbage if compression failed
}
```

GOOD:
```cpp
std::vector<char> compress(const std::string& input) {
    std::vector<char> compressed(ZSTD_compressBound(input.size()));
    size_t result = ZSTD_compress(compressed.data(), compressed.size(), input.data(), input.size(), 1);
    if (ZSTD_isError(result)) {
        throw std::runtime_error(ZSTD_getErrorName(result));
    }
    compressed.resize(result);
    return compressed;
}
```

**Pitfall 2: Ignoring content size for decompression**

BAD:
```cpp
std::string decompress(const std::vector<char>& compressed) {
    std::string result(1024*1024, '\0'); // Arbitrary size
    ZSTD_decompress(result.data(), result.size(), compressed.data(), compressed.size());
    return result;
}
```

GOOD:
```cpp
std::string decompress(const std::vector<char>& compressed) {
    unsigned long long original_size = ZSTD_getFrameContentSize(compressed.data(), compressed.size());
    if (original_size == ZSTD_CONTENTSIZE_UNKNOWN) {
        // Use streaming decompression for unknown size
        return streaming_decompress(compressed);
    }
    if (original_size == ZSTD_CONTENTSIZE_ERROR) {
        throw std::runtime_error("Invalid compressed data");
    }
    std::string result(original_size, '\0');
    size_t actual = ZSTD_decompress(result.data(), result.size(), compressed.data(), compressed.size());
    if (ZSTD_isError(actual)) throw std::runtime_error(ZSTD_getErrorName(actual));
    return result;
}
```

**Pitfall 3: Not resetting streaming contexts for reuse**

BAD:
```cpp
ZSTD_CCtx* cctx = ZSTD_createCCtx();
compress_stream(cctx, data1);
compress_stream(cctx, data2); // Context still has state from first compression
```

GOOD:
```cpp
ZSTD_CCtx* cctx = ZSTD_createCCtx();
compress_stream(cctx, data1);
ZSTD_CCtx_reset(cctx, ZSTD_reset_session_only); // Reset for next use
compress_stream(cctx, data2);
```

**Pitfall 4: Using wrong buffer sizes for streaming**

BAD:
```cpp
void compress_stream(ZSTD_CCtx* cctx, const std::string& input) {
    std::vector<char> out_buf(1024); // Too small, may cause many iterations
    ZSTD_inBuffer in = {input.data(), input.size(), 0};
    ZSTD_outBuffer out = {out_buf.data(), out_buf.size(), 0};
    ZSTD_compressStream2(cctx, &out, &in, ZSTD_e_end);
}
```

GOOD:
```cpp
void compress_stream(ZSTD_CCtx* cctx, const std::string& input) {
    std::vector<char> out_buf(ZSTD_CStreamOutSize()); // Recommended size
    ZSTD_inBuffer in = {input.data(), input.size(), 0};
    ZSTD_outBuffer out = {out_buf.data(), out_buf.size(), 0};
    while (in.pos < in.size) {
        ZSTD_compressStream2(cctx, &out, &in, ZSTD_e_continue);
        // Process out_buf up to out.pos
        out.pos = 0;
    }
    do {
        ZSTD_compressStream2(cctx, &out, &in, ZSTD_e_end);
        // Process remaining data
        out.pos = 0;
    } while (out.pos > 0);
}
```

**Pitfall 5: Not handling dictionary training failures**

BAD:
```cpp
std::vector<char> train_dict(const std::vector<std::string>& samples) {
    std::vector<char> dict(100000);
    ZDICT_trainFromBuffer(dict.data(), dict.size(), samples.data(), sizes.data(), sizes.size());
    return dict; // Might contain garbage if training failed
}
```

GOOD:
```cpp
std::vector<char> train_dict(const std::vector<std::string>& samples) {
    std::vector<size_t> sizes;
    std::vector<char> all_data;
    for (const auto& s : samples) {
        sizes.push_back(s.size());
        all_data.insert(all_data.end(), s.begin(), s.end());
    }
    std::vector<char> dict(100000);
    size_t result = ZDICT_trainFromBuffer(dict.data(), dict.size(), all_data.data(), sizes.data(), sizes.size());
    if (ZDICT_isError(result)) {
        throw std::runtime_error(ZDICT_getErrorName(result));
    }
    dict.resize(result);
    return dict;
}
```

**Pitfall 6: Memory leaks from not freeing contexts**

BAD:
```cpp
void process_data(const std::string& data) {
    ZSTD_CCtx* cctx = ZSTD_createCCtx();
    // Use cctx...
    // Forgot to call ZSTD_freeCCtx(cctx);
}
```

GOOD:
```cpp
void process_data(const std::string& data) {
    ZSTD_CCtx* cctx = ZSTD_createCCtx();
    if (!cctx) throw std::runtime_error("Failed to create context");
    // Use cctx...
    ZSTD_freeCCtx(cctx); // Always free
}
```