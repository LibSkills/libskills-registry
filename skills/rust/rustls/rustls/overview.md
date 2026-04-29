# Overview

`rustls/rustls` is a modern, memory-safe TLS library written in Rust that provides a C++ API for secure network communication. It implements TLS 1.2 and 1.3 protocols with a focus on safety, performance, and ease of use.

**When to use:**
- Building secure client-server applications requiring TLS encryption
- Implementing HTTPS, WebSockets, or other secure protocols
- Applications where memory safety is critical (avoiding OpenSSL's C-based vulnerabilities)
- Projects needing modern TLS 1.3 support with forward secrecy
- Embedded systems or environments where binary size matters

**When not to use:**
- Legacy systems requiring SSL 3.0 or TLS 1.0/1.1 support (rustls only supports TLS 1.2+)
- Environments requiring FIPS 140-2 compliance (rustls is not FIPS certified)
- Applications needing custom cipher suites not supported by rustls
- Projects that must use system certificate stores on Windows (rustls uses its own certificate handling)

**Key design principles:**
- Memory safety: Built on Rust's ownership model, preventing buffer overflows and use-after-free
- No unsafe code: The core library contains zero `unsafe` Rust code
- Modern cryptography: Uses only modern, audited cryptographic primitives
- Minimal dependencies: Reduces attack surface and binary size
- Clear error handling: Returns explicit error types rather than relying on errno or global state