# Safety

```cpp
// RED LINE 1: NEVER call AWS APIs before InitAPI or after ShutdownAPI
// BAD: Using client before initialization
void unsafeInit() {
    Aws::S3::S3Client client;  // Undefined behavior
    // SDK not initialized
}

// GOOD: Always initialize first
void safeInit() {
    Aws::SDKOptions options;
    Aws::InitAPI(options);
    {
        Aws::S3::S3Client client;
        // Safe to use
    }
    Aws::ShutdownAPI(options);
}

// RED LINE 2: NEVER access outcome result without checking success
// BAD: Direct access without check
void unsafeOutcome() {
    auto outcome = client.ListBuckets();
    auto buckets = outcome.GetResult().GetBuckets();  // CRASH if failed
}

// GOOD: Always check IsSuccess()
void safeOutcome() {
    auto outcome = client.ListBuckets();
    if (outcome.IsSuccess()) {
        auto buckets = outcome.GetResult().GetBuckets();
    } else {
        // Handle error
    }
}

// RED LINE 3: NEVER modify client configuration after construction
// BAD: Changing config after creation
void unsafeConfig(Aws::S3::S3Client& client) {
    client.SetRegion("us-west-2");  // Thread-unsafe
}

// GOOD: Set config at construction
void safeConfig() {
    Aws::Client::ClientConfiguration config;
    config.region = "us-west-2";
    Aws::S3::S3Client client(config);
}

// RED LINE 4: NEVER use std::make_shared with AWS SDK objects
// BAD: Using standard allocator
void unsafeAllocator() {
    auto stream = std::make_shared<Aws::FStream>("file.txt", std::ios::in);
    // Memory not tracked by SDK
}

// GOOD: Use SDK allocator
void safeAllocator() {
    auto stream = Aws::MakeShared<Aws::FStream>("MyTag", "file.txt", std::ios::in);
}

// RED LINE 5: NEVER call ShutdownAPI while operations are in flight
// BAD: Shutting down with active operations
void unsafeShutdown() {
    Aws::SDKOptions options;
    Aws::InitAPI(options);
    auto future = std::async(std::launch::async, [&]() {
        Aws::S3::S3Client client;
        client.ListBuckets();  // May still be running
    });
    Aws::ShutdownAPI(options);  // CRASH: operations still active
    future.wait();
}

// GOOD: Ensure all operations complete before shutdown
void safeShutdown() {
    Aws::SDKOptions options;
    Aws::InitAPI(options);
    {
        Aws::S3::S3Client client;
        auto outcome = client.ListBuckets();
        // Wait for completion
    }
    Aws::ShutdownAPI(options);  // Safe: no active operations
}
```