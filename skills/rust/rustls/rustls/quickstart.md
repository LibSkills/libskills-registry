# Quickstart

```cpp
// Example 1: Basic TLS client connection
#include <rustls/rustls.h>
#include <iostream>
#include <string>

int main() {
    // Create a client config with default settings
    rustls::ClientConfig config;
    config.set_ca_file("/etc/ssl/certs/ca-certificates.crt");
    
    // Create a TLS connection
    rustls::ClientConnection conn(config, "example.com");
    
    // Perform handshake
    conn.do_handshake();
    
    // Send data
    std::string request = "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n";
    conn.write(request.data(), request.size());
    
    // Read response
    char buffer[4096];
    size_t bytes_read = conn.read(buffer, sizeof(buffer));
    std::cout << std::string(buffer, bytes_read) << std::endl;
    
    return 0;
}

// Example 2: TLS server with self-signed certificate
#include <rustls/rustls.h>
#include <fstream>
#include <vector>

int main() {
    // Load certificate and private key
    std::ifstream cert_file("server.crt");
    std::string cert((std::istreambuf_iterator<char>(cert_file)),
                      std::istreambuf_iterator<char>());
    
    std::ifstream key_file("server.key");
    std::string key((std::istreambuf_iterator<char>(key_file)),
                     std::istreambuf_iterator<char>());
    
    // Create server config
    rustls::ServerConfig config;
    config.set_certificate(cert);
    config.set_private_key(key);
    
    // Accept a connection
    rustls::ServerConnection conn(config);
    conn.do_handshake();
    
    // Read and write data
    char buffer[4096];
    size_t bytes_read = conn.read(buffer, sizeof(buffer));
    conn.write("Hello, client!", 14);
    
    return 0;
}

// Example 3: Async TLS connection with callbacks
#include <rustls/rustls.h>
#include <functional>

class MySession {
public:
    void on_data(const uint8_t* data, size_t len) {
        // Process received data
        std::cout << "Received " << len << " bytes" << std::endl;
    }
    
    void on_error(const std::string& msg) {
        std::cerr << "TLS error: " << msg << std::endl;
    }
};

int main() {
    rustls::ClientConfig config;
    config.set_ca_file("/etc/ssl/certs/ca-certificates.crt");
    
    MySession session;
    rustls::ClientConnection conn(config, "example.com");
    
    // Set callbacks
    conn.set_data_callback([&session](const uint8_t* data, size_t len) {
        session.on_data(data, len);
    });
    conn.set_error_callback([&session](const std::string& msg) {
        session.on_error(msg);
    });
    
    // Start async handshake
    conn.start_handshake();
    
    return 0;
}

// Example 4: Custom certificate verification
#include <rustls/rustls.h>
#include <vector>

bool verify_certificate(const std::vector<uint8_t>& cert_der) {
    // Custom verification logic
    // Return true if certificate is trusted
    return true;
}

int main() {
    rustls::ClientConfig config;
    config.set_certificate_verifier(verify_certificate);
    config.set_ca_file("/etc/ssl/certs/ca-certificates.crt");
    
    rustls::ClientConnection conn(config, "example.com");
    conn.do_handshake();
    
    return 0;
}

// Example 5: Session resumption
#include <rustls/rustls.h>
#include <vector>

int main() {
    rustls::ClientConfig config;
    config.set_ca_file("/etc/ssl/certs/ca-certificates.crt");
    
    // First connection
    rustls::ClientConnection conn1(config, "example.com");
    conn1.do_handshake();
    
    // Save session ticket
    std::vector<uint8_t> session_ticket = conn1.get_session_ticket();
    
    // Second connection with resumption
    rustls::ClientConnection conn2(config, "example.com");
    conn2.set_session_ticket(session_ticket);
    conn2.do_handshake(); // Faster handshake
    
    return 0;
}

// Example 6: ALPN protocol negotiation
#include <rustls/rustls.h>
#include <vector>
#include <string>

int main() {
    rustls::ClientConfig config;
    config.set_ca_file("/etc/ssl/certs/ca-certificates.crt");
    config.set_alpn_protocols({"h2", "http/1.1"});
    
    rustls::ClientConnection conn(config, "example.com");
    conn.do_handshake();
    
    // Check negotiated protocol
    std::string negotiated = conn.get_alpn_protocol();
    std::cout << "Negotiated: " << negotiated << std::endl;
    
    return 0;
}

// Example 7: Mutual TLS authentication
#include <rustls/rustls.h>
#include <fstream>

int main() {
    // Load client certificate and key
    std::ifstream client_cert_file("client.crt");
    std::string client_cert((std::istreambuf_iterator<char>(client_cert_file)),
                             std::istreambuf_iterator<char>());
    
    std::ifstream client_key_file("client.key");
    std::string client_key((std::istreambuf_iterator<char>(client_key_file)),
                            std::istreambuf_iterator<char>());
    
    rustls::ClientConfig config;
    config.set_ca_file("/etc/ssl/certs/ca-certificates.crt");
    config.set_client_certificate(client_cert, client_key);
    
    rustls::ClientConnection conn(config, "example.com");
    conn.do_handshake();
    
    return 0;
}

// Example 8: Connection with timeout
#include <rustls/rustls.h>
#include <chrono>
#include <thread>

int main() {
    rustls::ClientConfig config;
    config.set_ca_file("/etc/ssl/certs/ca-certificates.crt");
    config.set_handshake_timeout(std::chrono::seconds(10));
    
    rustls::ClientConnection conn(config, "example.com");
    
    // Attempt handshake with timeout
    if (conn.do_handshake_with_timeout(std::chrono::seconds(5))) {
        std::cout << "Handshake successful" << std::endl;
    } else {
        std::cerr << "Handshake timed out" << std::endl;
    }
    
    return 0;
}
```