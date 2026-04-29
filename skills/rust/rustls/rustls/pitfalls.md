# Pitfalls

```cpp
// PITFALL 1: Not checking handshake result
// BAD: Ignoring handshake failure
rustls::ClientConnection conn(config, "example.com");
conn.do_handshake(); // May silently fail

// GOOD: Always check handshake result
rustls::ClientConnection conn(config, "example.com");
if (!conn.do_handshake()) {
    std::cerr << "Handshake failed: " << conn.last_error() << std::endl;
    return;
}

// PITFALL 2: Using expired or invalid certificates
// BAD: Loading certificate without validation
std::string cert = load_file("expired.crt");
config.set_certificate(cert); // May accept expired cert

// GOOD: Validate certificate before loading
std::string cert = load_file("valid.crt");
if (!rustls::Certificate::is_valid(cert)) {
    std::cerr << "Certificate is expired or invalid" << std::endl;
    return;
}
config.set_certificate(cert);

// PITFALL 3: Mixing sync and async operations
// BAD: Calling read after async write
conn.start_async_write(data, len);
size_t bytes = conn.read(buffer, sizeof(buffer)); // Undefined behavior

// GOOD: Use consistent mode
conn.start_async_write(data, len);
conn.wait_for_completion();
size_t bytes = conn.read(buffer, sizeof(buffer));

// PITFALL 4: Not handling partial reads/writes
// BAD: Assuming single read gets all data
char buffer[4096];
size_t bytes = conn.read(buffer, sizeof(buffer));
process_data(buffer, bytes); // May miss data

// GOOD: Loop until all data received
std::string data;
char buffer[4096];
while (conn.has_pending_data()) {
    size_t bytes = conn.read(buffer, sizeof(buffer));
    data.append(buffer, bytes);
}

// PITFALL 5: Ignoring connection state changes
// BAD: Not checking if connection is still alive
conn.write(data, len); // May fail silently if closed

// GOOD: Check connection state before operations
if (conn.is_closed()) {
    std::cerr << "Connection already closed" << std::endl;
    return;
}
if (!conn.write(data, len)) {
    std::cerr << "Write failed, connection may be closed" << std::endl;
}

// PITFALL 6: Incorrect certificate chain ordering
// BAD: Providing certificates in wrong order
config.set_certificate_chain({intermediate_cert, root_cert, leaf_cert});

// GOOD: Provide chain in correct order (leaf first)
config.set_certificate_chain({leaf_cert, intermediate_cert, root_cert});

// PITFALL 7: Not setting proper ALPN protocols
// BAD: Empty ALPN list
config.set_alpn_protocols({}); // May negotiate unexpected protocol

// GOOD: Specify expected protocols
config.set_alpn_protocols({"h2", "http/1.1"});

// PITFALL 8: Using default config without customization
// BAD: Using default config for production
rustls::ClientConfig config; // May be too permissive

// GOOD: Configure security settings explicitly
rustls::ClientConfig config;
config.set_min_tls_version(rustls::TLSVersion::TLS_1_2);
config.set_cipher_suites({rustls::CipherSuite::TLS_AES_128_GCM_SHA256});
config.set_ca_file("/etc/ssl/certs/ca-certificates.crt");
```