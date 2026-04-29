# Best Practices

```cpp
#include <snappy.h>
#include <string>
#include <vector>
#include <stdexcept>
#include <optional>

// Best Practice 1: RAII wrapper for compression
class SnappyCompressor {
public:
    static std::string compress(const std::string& input) {
        if (input.empty()) return {};
        
        std::string output;
        output.resize(snappy::MaxCompressedLength(input.size()));
        
        size_t compressed_size;
        snappy::RawCompress(input.data(), input.size(), 
                           output.data(), &compressed_size);
        output.resize(compressed_size);
        return output;
    }
    
    static std::optional<std::string> decompress(const std::string& input) {
        if (input.empty()) return std::string{};
        
        if (!snappy::IsValidCompressedBuffer(input.data(), input.size())) {
            return std::nullopt;
        }
        
        size_t uncompressed_size;
        if (!snappy::GetUncompressedLength(input.data(), input.size(), 
                                           &uncompressed_size)) {
            return std::nullopt;
        }
        
        std::string output;
        output.resize(uncompressed_size);
        
        if (!snappy::RawUncompress(input.data(), input.size(), 
                                   output.data())) {
            return std::nullopt;
        }
        
        return output;
    }
};

// Best Practice 2: Compression with size threshold
class SmartCompressor {
    static constexpr size_t MIN_COMPRESSION_SIZE = 100;
    
public:
    struct CompressedData {
        std::string data;
        bool is_compressed;
    };
    
    static CompressedData compress(const std::string& input) {
        if (input.size() < MIN_COMPRESSION_SIZE) {
            return {input, false};  // Too small to compress
        }
        
        std::string compressed;
        compressed.resize(snappy::MaxCompressedLength(input.size()));
        
        size_t compressed_size;
        snappy::RawCompress(input.data(), input.size(), 
                           compressed.data(), &compressed_size);
        compressed.resize(compressed_size);
        
        if (compressed.size() >= input.size()) {
            return {input, false};  // Compression didn't help
        }
        
        return {compressed, true};
    }
    
    static std::string decompress(const CompressedData& data) {
        if (!data.is_compressed) {
            return data.data;
        }
        
        auto result = SnappyCompressor::decompress(data.data);
        if (!result) {
            throw std::runtime_error("Decompression failed");
        }
        return *result;
    }
};

// Best Practice 3: Batch compression for network packets
class PacketCompressor {
    static constexpr size_t MAX_PACKET_SIZE = 65536;
    
public:
    struct Packet {
        std::vector<char> data;
        size_t original_size;
    };
    
    static Packet compress_packet(const std::vector<char>& raw_data) {
        if (raw_data.size() > MAX_PACKET_SIZE) {
            throw std::length_error("Packet too large");
        }
        
        Packet packet;
        packet.original_size = raw_data.size();
        packet.data.resize(snappy::MaxCompressedLength(raw_data.size()));
        
        size_t compressed_size;
        snappy::RawCompress(raw_data.data(), raw_data.size(),
                           packet.data.data(), &compressed_size);
        packet.data.resize(compressed_size);
        
        return packet;
    }
    
    static std::vector<char> decompress_packet(const Packet& packet) {
        std::vector<char> result(packet.original_size);
        
        if (!snappy::RawUncompress(packet.data.data(), packet.data.size(),
                                   result.data())) {
            throw std::runtime_error("Packet decompression failed");
        }
        
        return result;
    }
};

// Best Practice 4: Memory-efficient streaming (for large data)
class StreamingCompressor {
    static constexpr size_t CHUNK_SIZE = 1024 * 1024;  // 1MB chunks
    
public:
    static std::vector<std::string> compress_stream(const std::string& input) {
        std::vector<std::string> chunks;
        
        for (size_t offset = 0; offset < input.size(); offset += CHUNK_SIZE) {
            size_t chunk_size = std::min(CHUNK_SIZE, input.size() - offset);
            std::string chunk = input.substr(offset, chunk_size);
            
            std::string compressed;
            compressed.resize(snappy::MaxCompressedLength(chunk_size));
            
            size_t compressed_size;
            snappy::RawCompress(chunk.data(), chunk.size(),
                               compressed.data(), &compressed_size);
            compressed.resize(compressed_size);
            chunks.push_back(std::move(compressed));
        }
        
        return chunks;
    }
    
    static std::string decompress_stream(const std::vector<std::string>& chunks) {
        std::string result;
        result.reserve(chunks.size() * CHUNK_SIZE);  // Estimate
        
        for (const auto& chunk : chunks) {
            size_t uncompressed_size;
            if (!snappy::GetUncompressedLength(chunk.data(), chunk.size(),
                                               &uncompressed_size)) {
                throw std::runtime_error("Invalid chunk");
            }
            
            size_t old_size = result.size();
            result.resize(old_size + uncompressed_size);
            
            if (!snappy::RawUncompress(chunk.data(), chunk.size(),
                                       result.data() + old_size)) {
                throw std::runtime_error("Chunk decompression failed");
            }
        }
        
        return result;
    }
};
```