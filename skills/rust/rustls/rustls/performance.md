# Performance

```cpp
// PERFORMANCE CHARACTERISTICS
// rustls is designed for high performance with:
// - Zero-copy buffer management where possible
// - Minimal memory allocations during steady state
// - Efficient session resumption for repeated connections

// ALLOCATION PATTERNS: Pre-allocate buffers
// BAD: Frequent small allocations
for (int i = 0; i < 1000; ++i) {
    char buffer[64]; // Stack allocation each iteration
    conn.read(buffer, sizeof(buffer));
}

// GOOD: Reuse buffers
std::vector<char> buffer(65536); // 64KB buffer
for (int i = 0; i < 1000; ++i) {
    size_t bytes = conn.read(buffer.data(), buffer.size());
    process_data(buffer.data(), bytes);
}

// OPTIMIZATION TIP 1: Use session resumption
// BAD: Full handshake every time
for (const auto& host : hosts) {
    rustls::ClientConnection conn(config, host);
    conn.do_handshake(); // Full handshake each time
}

// GOOD: Reuse session tickets
std::unordered_map<std::string, std::vector<uint8_t>> session_cache;
for (const auto& host : hosts) {
    rustls::ClientConnection conn(config, host);
    
    auto it = session_cache.find(host);
    if (it != session_cache.end()) {
        conn.set_session_ticket(it->second);
    }
    
    conn.do_handshake(); // May be faster with resumption
    
    session_cache[host] = conn.get_session_ticket();
}

// OPTIMIZATION TIP 2: Batch writes
// BAD: Many small writes
for (const auto& chunk : small_chunks) {
    conn.write(chunk.data(), chunk.size()); // Many syscalls
}

// GOOD: Batch data before writing
std::string buffer;
for (const auto& chunk : small_chunks) {
    buffer += chunk;
}
conn.write(buffer.data(), buffer.size()); // Single write

// OPTIMIZATION TIP 3: Use non-blocking I/O
// BAD: Blocking reads
char buffer[4096];
while (true) {
    size_t bytes = conn.read(buffer, sizeof(buffer)); // Blocks
    if (bytes == 0) break;
    process_data(buffer, bytes);
}

// GOOD: Non-blocking with event loop
conn.set_nonblocking(true);
char buffer[4096];
while (true) {
    if (conn.has_pending_data()) {
        size_t bytes = conn.read(buffer, sizeof(buffer));
        process_data(buffer, bytes);
    }
    // Do other work or yield
    std::this_thread::yield();
}

// OPTIMIZATION TIP 4: Configure buffer sizes
// BAD: Default buffer sizes
rustls::ClientConfig config;
rustls::ClientConnection conn(config, "example.com");

// GOOD: Tune buffer sizes for your workload
rustls::ClientConfig config;
config.set_read_buffer_size(65536);  // 64KB read buffer
config.set_write_buffer_size(65536); // 64KB write buffer
config.set_max_fragment_size(16384); // Maximum TLS fragment size

rustls::ClientConnection conn(config, "example.com");

// OPTIMIZATION TIP 5: Use connection pooling
// BAD: Creating new connections frequently
for (int i = 0; i < 100; ++i) {
    rustls::ClientConnection conn(config, "example.com");
    conn.do_handshake();
    conn.write(request.data(), request.size());
    // Connection destroyed
}

// GOOD: Reuse connections
class ConnectionPool {
    std::vector<std::unique_ptr<rustls::ClientConnection>> connections_;
    
public:
    rustls::ClientConnection* get() {
        if (!connections_.empty()) {
            auto conn = std::move(connections_.back());
            connections_.pop_back();
            return conn.release();
        }
        return new rustls::ClientConnection(config_, "example.com");
    }
    
    void put(rustls::ClientConnection* conn) {
        connections_.push_back(std::unique_ptr<rustls::ClientConnection>(conn));
    }
};

// OPTIMIZATION TIP 6: Profile with realistic workloads
#include <chrono>

void benchmark_connection() {
    auto start = std::chrono::high_resolution_clock::now();
    
    rustls::ClientConnection conn(config, "example.com");
    conn.do_handshake();
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    std::cout << "Handshake took " << duration.count() << " microseconds" << std::endl;
}
```