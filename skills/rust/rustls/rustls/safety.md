# Safety

```cpp
// SAFETY CONDITION 1: NEVER use the same connection object concurrently
// BAD: Concurrent read/write from different threads
std::thread reader([&conn]() {
    char buffer[1024];
    conn.read(buffer, sizeof(buffer)); // Race condition
});
std::thread writer([&conn]() {
    conn.write("data", 4); // Race condition
});

// GOOD: Serialize access or use separate connections
std::mutex mtx;
std::thread reader([&conn, &mtx]() {
    std::lock_guard<std::mutex> lock(mtx);
    char buffer[1024];
    conn.read(buffer, sizeof(buffer));
});
std::thread writer([&conn, &mtx]() {
    std::lock_guard<std::mutex> lock(mtx);
    conn.write("data", 4);
});

// SAFETY CONDITION 2: NEVER pass invalid pointers to read/write
// BAD: Using dangling pointer
char* buffer = new char[1024];
delete[] buffer;
conn.read(buffer, 1024); // Use-after-free

// GOOD: Use valid memory
std::vector<char> buffer(1024);
conn.read(buffer.data(), buffer.size());

// SAFETY CONDITION 3: NEVER ignore error return values
// BAD: Ignoring return value
conn.do_handshake(); // May fail silently

// GOOD: Always check return values
if (!conn.do_handshake()) {
    throw std::runtime_error("Handshake failed: " + conn.last_error());
}

// SAFETY CONDITION 4: NEVER use after connection is closed
// BAD: Using closed connection
conn.close();
conn.write("data", 4); // Undefined behavior

// GOOD: Check state before operations
if (!conn.is_closed()) {
    conn.write("data", 4);
} else {
    // Handle closed connection
}

// SAFETY CONDITION 5: NEVER mix different TLS library instances
// BAD: Using rustls connection with OpenSSL context
rustls::ClientConnection conn(config, "example.com");
SSL* ssl = conn.get_internal_ssl(); // Not supported
SSL_do_handshake(ssl); // Undefined behavior

// GOOD: Use rustls API exclusively
rustls::ClientConnection conn(config, "example.com");
conn.do_handshake();
```