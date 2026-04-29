# Best Practices

**Use RAII wrappers for contexts**

```cpp
class ZstdCompressor {
    ZSTD_CCtx* cctx_;
public:
    ZstdCompressor(int level = 3) {
        cctx_ = ZSTD_createCCtx();
        if (!cctx_) throw std::runtime_error("Failed to create compressor");
        ZSTD_CCtx_setParameter(cctx_, ZSTD_c_compressionLevel, level);
    }
    ~ZstdCompressor() { if (cctx_) ZSTD_freeCCtx(cctx_); }
    ZstdCompressor(const ZstdCompressor&) = delete;
    ZstdCompressor& operator=(const ZstdCompressor&) = delete;
    ZstdCompressor(ZstdCompressor&& other) noexcept : cctx_(other.cctx_) { other.cctx_ = nullptr; }
    
    std::vector<char> compress(const std::string& input) {
        size_t max_size = ZSTD_compressBound(input.size());
        std::vector<char> output(max_size);
        size_t actual = ZSTD_compress2(cctx_, output.data(), output.size(), input.data(), input.size());
        if (ZSTD_isError(actual)) throw std::runtime_error(ZSTD_getErrorName(actual));
        output.resize(actual);
        return output;
    }
};
```

**Prefer ZSTD_compress2 over ZSTD_compress for parameterized compression**

```cpp
// GOOD: Use ZSTD_compress2 for explicit parameter control
ZSTD_CCtx* cctx = ZSTD_createCCtx();
ZSTD_CCtx_setParameter(cctx, ZSTD_c_compressionLevel, 5);
ZSTD_CCtx_setParameter(cctx, ZSTD_c_checksumFlag, 1);
size_t result = ZSTD_compress2(cctx, out.data(), out.size(), in.data(), in.size());
```

**Use streaming API for large data or unknown sizes**

```cpp
class StreamingDecompressor {
    ZSTD_DCtx* dctx_;
    std::vector<char> buffer_;
public:
    StreamingDecompressor() : dctx_(ZSTD_createDCtx()), buffer_(ZSTD_DStreamOutSize()) {
        if (!dctx_) throw std::runtime_error("Failed to create decompressor");
    }
    ~StreamingDecompressor() { if (dctx_) ZSTD_freeDCtx(dctx_); }
    
    std::string decompress_chunk(const char* data, size_t size, bool is_last) {
        ZSTD_inBuffer in = {data, size, 0};
        ZSTD_outBuffer out = {buffer_.data(), buffer_.size(), 0};
        std::string result;
        
        while (in.pos < in.size) {
            ZSTD_endDirective end = is_last ? ZSTD_e_end : ZSTD_e_continue;
            size_t ret = ZSTD_decompressStream(dctx_, &out, &in);
            if (ZSTD_isError(ret)) throw std::runtime_error(ZSTD_getErrorName(ret));
            result.append(buffer_.data(), out.pos);
            out.pos = 0;
            if (ret == 0) break; // Frame complete
        }
        return result;
    }
};
```

**Always validate dictionary before use**

```cpp
bool validate_dictionary(const std::vector<char>& dict) {
    if (dict.empty()) return false;
    // Check magic number for Zstd dictionary
    if (dict.size() < 4) return false;
    uint32_t magic = *reinterpret_cast<const uint32_t*>(dict.data());
    return magic == 0xEC30A437; // Zstd dictionary magic number
}
```