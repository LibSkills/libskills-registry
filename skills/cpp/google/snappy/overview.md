# Overview

Snappy is a fast compression/decompression library developed by Google. It prioritizes speed over compression ratio, making it ideal for real-time applications where throughput matters more than storage efficiency.

**When to use Snappy:**
- Real-time data compression in network protocols
- Caching systems where compression speed is critical
- Database storage engines (e.g., LevelDB, RocksDB)
- Log file compression
- Any scenario requiring fast compression with moderate compression ratios

**When NOT to use Snappy:**
- When maximum compression ratio is required (use zstd, bzip2, or LZMA instead)
- For archiving or long-term storage where size matters more than speed
- When streaming compression is needed (Snappy works on complete buffers)
- For very small data (< 100 bytes) where overhead may exceed benefits

**Key Design:**
- LZ77-based compression with fixed Huffman coding
- No entropy encoding (no arithmetic coding or adaptive Huffman)
- Maximum compression ratio is typically 2:1 to 5:1 for text data
- Guaranteed maximum expansion of 1.6x for incompressible data
- Deterministic: same input always produces same output
- No memory allocation during compression/decompression (uses caller-provided buffers)