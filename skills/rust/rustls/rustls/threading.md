# Threading

```cpp
// THREAD SAFETY GUARANTEES
// rustls connections are NOT thread-safe by default
// Each connection object must be used from a single thread at a time
// Config objects are thread-safe for reading after construction

// SAFE: Single-threaded usage
void single_thread_example() {
    rustls::ClientConnection conn(config, "example.com");
    conn.do_handshake();
    conn.write("data", 4);
    char buffer[1024];
    conn.read(buffer, sizeof(buffer));
}

// UNSAFE: Concurrent access from multiple threads
void unsafe_example() {
    rustls::ClientConnection conn(config, "example.com");
    
    std::thread t1([&conn]() {
        conn.write("data1", 5); // Race condition
    });
    
    std::thread t2([&conn]() {
        conn.write("data2", 5); // Race condition
    });
    
    t1.join();
    t2.join();
}

// SAFE: Thread-safe wrapper with mutex
class ThreadSafeConnection {
    rustls::ClientConnection conn_;
    std::mutex mtx_;
    
public:
    ThreadSafeConnection(const rustls::ClientConfig& config, const std::string& host)
        : conn_(config, host) {}
    
    bool write(const std::string& data) {
        std::lock_guard<std::mutex> lock(mtx_);
        return conn_.write(data.data(), data.size());
    }
    
    std::string read(size_t max_size) {
        std::lock_guard<std::mutex> lock(mtx_);
        std::vector<char> buffer(max_size);
        size_t bytes = conn_.read(buffer.data(), buffer.size());
        return std::string(buffer.data(), bytes);
    }
    
    bool do_handshake() {
        std::lock_guard<std::mutex> lock(mtx_);
        return conn_.do_handshake();
    }
};

// SAFE: Thread-local connections
class ThreadLocalConnectionPool {
    static thread_local std::unique_ptr<rustls::ClientConnection> tls_conn;
    
public:
    rustls::ClientConnection& get() {
        if (!tls_conn) {
            tls_conn = std::make_unique<rustls::ClientConnection>(config_, "example.com");
            tls_conn->do_handshake();
        }
        return *tls_conn;
    }
};

thread_local std::unique_ptr<rustls::ClientConnection> 
    ThreadLocalConnectionPool::tls_conn;

// SAFE: Read-only config sharing
rustls::ClientConfig create_shared_config() {
    rustls::ClientConfig config;
    config.set_ca_file("/etc/ssl/certs/ca-certificates.crt");
    config.set_min_tls_version(rustls::TLSVersion::TLS_1_2);
    return config;
}

// Config is safe to share for reading
const auto& shared_config = create_shared_config();

void worker_thread() {
    // Each thread creates its own connection from shared config
    rustls::ClientConnection conn(shared_config, "example.com");
    conn.do_handshake();
}

// UNSAFE: Modifying config while connections exist
void unsafe_config_modification() {
    rustls::ClientConfig config;
    config.set_ca_file("/etc/ssl/certs/ca-certificates.crt");
    
    rustls::ClientConnection conn(config, "example.com");
    
    // UNSAFE: Modifying config while connection exists
    config.set_ca_file("/different/ca.crt"); // Undefined behavior
}

// SAFE: Using connection pools with thread safety
class ThreadSafeConnectionPool {
    std::vector<std::unique_ptr<rustls::ClientConnection>> pool_;
    std::mutex pool_mtx_;
    std::condition_variable cv_;
    
public:
    std::unique_ptr<rustls::ClientConnection, std::function<void(rustls::ClientConnection*)>> 
    acquire() {
        std::unique_lock<std::mutex> lock(pool_mtx_);
        cv_.wait(lock, [this]() { return !pool_.empty(); });
        
        auto conn = std::move(pool_.back());
        pool_.pop_back();
        
        return std::unique_ptr<rustls::ClientConnection, 
                               std::function<void(rustls::ClientConnection*)>>(
            conn.release(),
            [this](rustls::ClientConnection* c) {
                std::lock_guard<std::mutex> lock(pool_mtx_);
                pool_.push_back(std::unique_ptr<rustls::ClientConnection>(c));
                cv_.notify_one();
            }
        );
    }
};

// SAFE: Async I/O with completion callbacks
class AsyncConnection {
    rustls::ClientConnection conn_;
    std::mutex mtx_;
    std::function<void(const std::string&)> callback_;
    
public:
    void async_read(std::function<void(const std::string&)> callback) {
        std::lock_guard<std::mutex> lock(mtx_);
        callback_ = std::move(callback);
        
        // Start async read operation
        conn_.start_async_read();
    }
    
    void on_read_complete() {
        std::lock_guard<std::mutex> lock(mtx_);
        if (callback_) {
            std::vector<char> buffer(4096);
            size_t bytes = conn_.read(buffer.data(), buffer.size());
            callback_(std::string(buffer.data(), bytes));
        }
    }
};
```