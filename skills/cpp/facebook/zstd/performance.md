# Performance

**Compression level trade-offs**

```cpp
// Level 1: Fastest compression, lower ratio
ZSTD_CCtx_setParameter(cctx, ZSTD_c_compressionLevel, 1);
// ~500 MB/s compression, ~2x ratio for text

// Level 3: Default, good balance
ZSTD_CCtx_setParameter(cctx, ZSTD_c_compressionLevel, 3);
// ~300 MB/s compression, ~3x ratio for text

// Level 19: Best compression, slow
ZSTD_CCtx_setParameter(cctx, ZSTD_c_compressionLevel, 19);
// ~10 MB/s compression, ~4x ratio for text

// Negative levels for ultra-fast modes
ZSTD_CCtx_setParameter(cctx, ZSTD_c_compressionLevel, -5);
// ~1000 MB/s compression, ~1.5x ratio
```

**Buffer size optimization**

```cpp
// Use recommended buffer sizes for streaming
const size_t in_buffer_size = ZSTD_CStreamInSize();  // ~128 KB
const size_t out_buffer_size = ZSTD_CStreamOutSize(); // ~128 KB

// For single-pass compression, use ZSTD_compressBound for output buffer
size_t max_output = ZSTD_compressBound(input_size);
// This guarantees enough space for any input
```

**Window size and memory usage**

```cpp
// Larger window = better compression but more memory
ZSTD_CCtx_setParameter(cctx, ZSTD_c_windowLog, 20); // 1 MB window
ZSTD_CCtx_setParameter(cctx, ZSTD_c_windowLog, 27); // 128 MB window (max)

// For decompression, memory usage depends on compressed data's window size
// Can be limited with:
ZSTD_DCtx_setParameter(dctx, ZSTD_d_windowLogMax, 20); // Limit to 1 MB
```

**Multi-threading for compression**

```cpp
// Enable multi-threaded compression
ZSTD_CCtx_setParameter(cctx, ZSTD_c_nbWorkers, 4); // Use 4 threads

// For large files, this can provide near-linear speedup
// Note: Decompression is always single-threaded
```

**Dictionary performance benefits**

```cpp
// For small data (< 1 KB), dictionaries can improve compression by 2-3x
// Training time: ~1 second for 1000 samples of 1 KB each
// Dictionary size: 100 KB typically provides good results

// Use dictionary for repeated patterns (e.g., JSON messages, log entries)
std::vector<char> dict = load_dictionary("my_dict.zstd");
ZSTD_CCtx_loadDictionary(cctx, dict.data(), dict.size());
// Compression of 100-byte messages: 80 bytes without dict, 30 bytes with dict
```