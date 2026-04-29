# Lifecycle

```cpp
// CONSTRUCTION: Creating TLS connections
#include <rustls/rustls.h>

// Default construction
rustls::ClientConfig config;
config.set_ca_file("/etc/ssl/certs/ca-certificates.crt");

// Parameterized construction
rustls::ClientConnection conn(config, "example.com");

// Construction with custom settings
rustls::ClientConfig secure_config;
secure_config.set_min_tls_version(rustls::TLSVersion::TLS_1_3);
secure_config.set_cipher_suites({rustls::CipherSuite::TLS_AES_256_GCM_SHA384});
rustls::ClientConnection secure_conn(secure_config, "secure.example.com");

// DESTRUCTION: Proper cleanup
{
    rustls::ClientConnection conn(config, "example.com");
    conn.do_handshake();
    // Connection automatically closes when going out of scope
} // Destructor called, resources freed

// Manual cleanup
rustls::ClientConnection* conn = new rustls::ClientConnection(config, "example.com");
conn->do_handshake();
delete conn; // Explicit cleanup

// MOVE SEMANTICS: Efficient transfer of ownership
rustls::ClientConnection conn1(config, "example.com");
conn1.do_handshake();

// Move construction
rustls::ClientConnection conn2(std::move(conn1)); // conn1 is now empty
// conn1 should not be used after move

// Move assignment
rustls::ClientConnection conn3(config, "other.com");
conn3 = std::move(conn2); // conn2 is now empty

// RESOURCE MANAGEMENT: Connection pooling
class ConnectionManager {
    std::vector<rustls::ClientConnection> pool_;
    
public:
    rustls::ClientConnection acquire(const std::string& host) {
        if (!pool_.empty()) {
            auto conn = std::move(pool_.back());
            pool_.pop_back();
            return conn;
        }
        
        rustls::ClientConnection conn(config_, host);
        conn.do_handshake();
        return conn;
    }
    
    void release(rustls::ClientConnection conn) {
        if (!conn.is_closed()) {
            pool_.push_back(std::move(conn));
        }
    }
};

// RESOURCE MANAGEMENT: Custom allocator support
struct TlsAllocator {
    void* allocate(size_t size) {
        return std::malloc(size);
    }
    
    void deallocate(void* ptr) {
        std::free(ptr);
    }
};

rustls::ClientConfig config_with_allocator;
config_with_allocator.set_allocator(std::make_shared<TlsAllocator>());

// LIFECYCLE EVENTS: Connection state machine
enum class ConnectionState {
    INITIAL,
    HANDSHAKING,
    CONNECTED,
    CLOSING,
    CLOSED
};

class StatefulConnection {
    rustls::ClientConnection conn_;
    ConnectionState state_ = ConnectionState::INITIAL;
    
public:
    void connect() {
        state_ = ConnectionState::HANDSHAKING;
        if (conn_.do_handshake()) {
            state_ = ConnectionState::CONNECTED;
        } else {
            state_ = ConnectionState::CLOSED;
        }
    }
    
    void close() {
        state_ = ConnectionState::CLOSING;
        conn_.close();
        state_ = ConnectionState::CLOSED;
    }
    
    ConnectionState get_state() const { return state_; }
};
```