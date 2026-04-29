# Lifecycle

**Construction and initialization**

```cpp
// Create compression context
ZSTD_CCtx* cctx = ZSTD_createCCtx();
if (!cctx) throw std::runtime_error("Failed to create compression context");

// Create decompression context
ZSTD_DCtx* dctx = ZSTD_createDCtx();
if (!dctx) throw std::runtime_error("Failed to create decompression context");

// Create streaming compression context
ZSTD_CStream* cstream = ZSTD_createCStream();
if (!cstream) throw std::runtime_error("Failed to create compression stream");

// Create streaming decompression context
ZSTD_DStream* dstream = ZSTD_createDStream();
if (!dstream) throw std::runtime_error("Failed to create decompression stream");
```

**Destruction and cleanup**

```cpp
// Always free contexts to avoid memory leaks
ZSTD_freeCCtx(cctx);
ZSTD_freeDCtx(dctx);
ZSTD_freeCStream(cstream);
ZSTD_freeDStream(dstream);

// Set to nullptr after freeing to prevent use-after-free
cctx = nullptr;
dctx = nullptr;
```

**Reset for reuse**

```cpp
// Reset compression context for new session (keeps parameters)
ZSTD_CCtx_reset(cctx, ZSTD_reset_session_only);

// Reset compression context including parameters
ZSTD_CCtx_reset(cctx, ZSTD_reset_session_and_parameters);

// Reset decompression context
ZSTD_DCtx_reset(dctx, ZSTD_reset_session_only);
```

**Move semantics with RAII wrapper**

```cpp
class ZstdContext {
    ZSTD_CCtx* ctx_;
public:
    ZstdContext(int level = 3) : ctx_(ZSTD_createCCtx()) {
        if (!ctx_) throw std::runtime_error("Failed to create context");
        ZSTD_CCtx_setParameter(ctx_, ZSTD_c_compressionLevel, level);
    }
    
    ~ZstdContext() { if (ctx_) ZSTD_freeCCtx(ctx_); }
    
    // Move constructor
    ZstdContext(ZstdContext&& other) noexcept : ctx_(other.ctx_) {
        other.ctx_ = nullptr;
    }
    
    // Move assignment
    ZstdContext& operator=(ZstdContext&& other) noexcept {
        if (this != &other) {
            if (ctx_) ZSTD_freeCCtx(ctx_);
            ctx_ = other.ctx_;
            other.ctx_ = nullptr;
        }
        return *this;
    }
    
    // Delete copy operations
    ZstdContext(const ZstdContext&) = delete;
    ZstdContext& operator=(const ZstdContext&) = delete;
    
    ZSTD_CCtx* get() const { return ctx_; }
};
```