# Overview

The AWS SDK for C++ provides a modern, object-oriented interface to Amazon Web Services. It wraps the AWS HTTP API with C++ abstractions, handling authentication, request signing, retries, and error handling automatically.

**When to use:**
- Building C++ applications that interact with AWS services (S3, DynamoDB, Lambda, etc.)
- Need high-performance AWS access with minimal overhead
- Working in environments where C++ is the primary language (game engines, embedded systems, high-frequency trading)
- Requiring fine-grained control over memory and threading

**When NOT to use:**
- Simple scripting tasks (use Python/boto3 instead)
- Web applications where latency isn't critical (use Java/Go SDKs)
- Prototyping or rapid development (Python SDK is more concise)
- Environments without C++17 support (requires C++11 or later)

**Key design principles:**
- RAII-based resource management with `Aws::SDKOptions` and `Aws::InitAPI`/`Aws::ShutdownAPI`
- Outcome-based error handling (not exceptions by default)
- Configurable HTTP client (curl-based by default, with custom implementations possible)
- Thread-safe client objects (can be shared across threads)
- Automatic request signing using AWS Signature V4
- Pluggable credential providers (environment variables, IAM roles, profile files)