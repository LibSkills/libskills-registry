# Best Practices

```cpp
// BEST PRACTICE 1: Use RAII wrappers for resource management
class TlsConnection {
    rustls::ClientConnection conn_;
public:
    TlsConnection(const rustls::ClientConfig& config, const std::string& host)
        : conn_(config, host) {
        if (!conn_.do_handshake()) {
            throw std::runtime_error("Handshake failed");
        }
    }
    
    ~TlsConnection() {
        if (!conn_.is_closed()) {
            conn_.close();
        }
    }
    
    // Prevent copying
    TlsConnection(const TlsConnection&) = delete;
    TlsConnection& operator=(const TlsConnection&) = delete;
    
    // Allow moving
    TlsConnection(TlsConnection&&) = default;
    TlsConnection& operator=(TlsConnection&&) = default;
};

// BEST PRACTICE 2: Implement proper error handling with retries
bool send_with_retry(rustls::ClientConnection& conn, 
                     const std::string& data, 
                     int max_retries = 3) {
    for (int i = 0; i < max_retries; ++i) {
        if (conn.write(data.data(), data.size())) {
            return true;
        }
        
        if (conn.is_closed()) {
            return false;
        }
        
        // Wait before retry
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    return false;
}

// BEST PRACTICE 3: Use connection pooling for multiple requests
class TlsConnectionPool {
    std::vector<std::unique_ptr<rustls::ClientConnection>> connections_;
    std::mutex mtx_;
    
public:
    rustls::ClientConnection* acquire(const std::string& host) {
        std::lock_guard<std::mutex> lock(mtx_);
        for (auto& conn : connections_) {
            if (!conn->is_closed() && conn->is_idle()) {
                conn->mark_busy();
                return conn.get();
            }
        }
        
        auto new_conn = std::make_unique<rustls::ClientConnection>(config_, host);
        if (new_conn->do_handshake()) {
            connections_.push_back(std::move(new_conn));
            return connections_.back().get();
        }
        return nullptr;
    }
    
    void release(rustls::ClientConnection* conn) {
        std::lock_guard<std::mutex> lock(mtx_);
        conn->mark_idle();
    }
};

// BEST PRACTICE 4: Implement proper certificate validation
class CertificateValidator {
public:
    static bool validate(const rustls::Certificate& cert) {
        // Check expiration
        if (cert.is_expired()) {
            return false;
        }
        
        // Check revocation status (OCSP)
        if (!cert.check_ocsp()) {
            return false;
        }
        
        // Check hostname match
        if (!cert.matches_hostname("example.com")) {
            return false;
        }
        
        return true;
    }
};

// BEST PRACTICE 5: Use async I/O for non-blocking operations
class AsyncTlsClient {
    rustls::ClientConnection conn_;
    std::function<void(const std::string&)> callback_;
    
public:
    void send_async(const std::string& data) {
        conn_.start_async_write(data.data(), data.size());
    }
    
    void on_data_ready() {
        std::vector<char> buffer(4096);
        size_t bytes = conn_.read(buffer.data(), buffer.size());
        if (bytes > 0 && callback_) {
            callback_(std::string(buffer.data(), bytes));
        }
    }
};

// BEST PRACTICE 6: Configure security settings explicitly
rustls::ClientConfig create_secure_config() {
    rustls::ClientConfig config;
    
    // Set minimum TLS version
    config.set_min_tls_version(rustls::TLSVersion::TLS_1_2);
    
    // Use strong cipher suites
    config.set_cipher_suites({
        rustls::CipherSuite::TLS_AES_256_GCM_SHA384,
        rustls::CipherSuite::TLS_CHACHA20_POLY1305_SHA256
    });
    
    // Enable certificate pinning
    config.set_certificate_pins({
        "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    });
    
    // Set reasonable timeouts
    config.set_handshake_timeout(std::chrono::seconds(10));
    config.set_idle_timeout(std::chrono::minutes(5));
    
    return config;
}
```