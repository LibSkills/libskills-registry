# Quickstart

```cpp
// Basic compression and decompression with Zstd
#include <zstd.h>
#include <vector>
#include <string>
#include <iostream>

// Example 1: Simple compression
std::vector<char> compress_data(const std::string& input) {
    size_t max_size = ZSTD_compressBound(input.size());
    std::vector<char> compressed(max_size);
    
    size_t actual_size = ZSTD_compress(compressed.data(), compressed.size(),
                                       input.data(), input.size(), 1);
    if (ZSTD_isError(actual_size)) {
        throw std::runtime_error(ZSTD_getErrorName(actual_size));
    }
    compressed.resize(actual_size);
    return compressed;
}

// Example 2: Simple decompression
std::string decompress_data(const std::vector<char>& compressed) {
    unsigned long long original_size = ZSTD_getFrameContentSize(compressed.data(), compressed.size());
    if (original_size == ZSTD_CONTENTSIZE_UNKNOWN || original_size == ZSTD_CONTENTSIZE_ERROR) {
        throw std::runtime_error("Unknown original size");
    }
    
    std::string decompressed(original_size, '\0');
    size_t actual_size = ZSTD_decompress(decompressed.data(), decompressed.size(),
                                         compressed.data(), compressed.size());
    if (ZSTD_isError(actual_size)) {
        throw std::runtime_error(ZSTD_getErrorName(actual_size));
    }
    return decompressed;
}

// Example 3: Streaming compression
void streaming_compress(const std::string& input, const std::string& output_file) {
    ZSTD_CCtx* cctx = ZSTD_createCCtx();
    if (!cctx) throw std::runtime_error("Failed to create compression context");
    
    FILE* out = fopen(output_file.c_str(), "wb");
    if (!out) { ZSTD_freeCCtx(cctx); throw std::runtime_error("Failed to open output file"); }
    
    ZSTD_inBuffer in_buf = {input.data(), input.size(), 0};
    std::vector<char> out_buf(ZSTD_CStreamOutSize());
    ZSTD_outBuffer out_buf_struct = {out_buf.data(), out_buf.size(), 0};
    
    while (in_buf.pos < in_buf.size) {
        ZSTD_compressStream2(cctx, &out_buf_struct, &in_buf, ZSTD_e_continue);
        fwrite(out_buf.data(), 1, out_buf_struct.pos, out);
        out_buf_struct.pos = 0;
    }
    
    do {
        ZSTD_compressStream2(cctx, &out_buf_struct, &in_buf, ZSTD_e_end);
        fwrite(out_buf.data(), 1, out_buf_struct.pos, out);
        out_buf_struct.pos = 0;
    } while (out_buf_struct.pos > 0);
    
    fclose(out);
    ZSTD_freeCCtx(cctx);
}

// Example 4: Streaming decompression
std::string streaming_decompress(const std::string& compressed) {
    ZSTD_DCtx* dctx = ZSTD_createDCtx();
    if (!dctx) throw std::runtime_error("Failed to create decompression context");
    
    std::string result;
    std::vector<char> out_buf(ZSTD_DStreamOutSize());
    ZSTD_inBuffer in_buf = {compressed.data(), compressed.size(), 0};
    ZSTD_outBuffer out_buf_struct = {out_buf.data(), out_buf.size(), 0};
    
    while (in_buf.pos < in_buf.size) {
        size_t ret = ZSTD_decompressStream(dctx, &out_buf_struct, &in_buf);
        if (ZSTD_isError(ret)) {
            ZSTD_freeDCtx(dctx);
            throw std::runtime_error(ZSTD_getErrorName(ret));
        }
        result.append(out_buf.data(), out_buf_struct.pos);
        out_buf_struct.pos = 0;
        if (ret == 0) break; // End of frame
    }
    
    ZSTD_freeDCtx(dctx);
    return result;
}

// Example 5: Using dictionary for better compression
std::vector<char> compress_with_dictionary(const std::string& input, const std::vector<char>& dict) {
    ZSTD_CCtx* cctx = ZSTD_createCCtx();
    ZSTD_CCtx_loadDictionary(cctx, dict.data(), dict.size());
    
    size_t max_size = ZSTD_compressBound(input.size());
    std::vector<char> compressed(max_size);
    
    size_t actual_size = ZSTD_compress2(cctx, compressed.data(), compressed.size(),
                                        input.data(), input.size());
    if (ZSTD_isError(actual_size)) {
        ZSTD_freeCCtx(cctx);
        throw std::runtime_error(ZSTD_getErrorName(actual_size));
    }
    compressed.resize(actual_size);
    ZSTD_freeCCtx(cctx);
    return compressed;
}

// Example 6: Training a dictionary
std::vector<char> train_dictionary(const std::vector<std::string>& samples, size_t dict_size = 100000) {
    std::vector<size_t> sizes;
    std::vector<char> all_data;
    for (const auto& s : samples) {
        sizes.push_back(s.size());
        all_data.insert(all_data.end(), s.begin(), s.end());
    }
    
    std::vector<char> dict(dict_size);
    ZDICT_trainFromBuffer(dict.data(), dict.size(), all_data.data(), sizes.data(), sizes.size());
    return dict;
}

int main() {
    std::string original = "Hello, World! This is a test of Zstd compression.";
    auto compressed = compress_data(original);
    auto decompressed = decompress_data(compressed);
    std::cout << "Original: " << original.size() << " bytes, Compressed: " 
              << compressed.size() << " bytes, Decompressed: " << decompressed.size() << " bytes\n";
    return 0;
}
```