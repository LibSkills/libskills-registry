# Overview

Zstd (Zstandard) is a real-time compression algorithm developed by Facebook that provides high compression ratios with fast speeds. It offers compression levels from 1 (fastest) to 22 (best compression), with level 3 being the default. The library supports both single-pass and streaming compression/decompression, dictionary-based compression for small data, and can be used as a drop-in replacement for zlib/gzip.

**When to use Zstd:**
- Need faster compression/decompression than zlib with comparable ratios
- Working with large datasets where streaming is beneficial
- Need dictionary-based compression for small messages (e.g., network protocols)
- Require compression levels that can be tuned for speed vs. ratio
- Want built-in checksumming and content size detection

**When NOT to use Zstd:**
- Need maximum compatibility (zlib/gzip are more universally supported)
- Working with extremely small data (< 100 bytes) where overhead matters
- Need patent-free algorithm (Zstd is covered by patents, though Facebook has a patent grant)
- Require hardware-accelerated compression (some platforms have specialized hardware for zlib)

**Key design features:**
- **Compression levels**: 1-22, with negative levels (-5 to -1) for ultra-fast modes
- **Streaming API**: ZSTD_CStream/ZSTD_DStream for processing data in chunks
- **Dictionary support**: Pre-trained dictionaries improve compression for small data
- **Content size detection**: Automatically detects original size from compressed data
- **Checksums**: Optional 32-bit checksum for data integrity
- **Multi-threading**: ZSTD_CCtx_setParameter with ZSTD_c_nbWorkers for parallel compression