# Pitfalls

```cpp
// PITFALL 1: Forgetting to initialize/shutdown SDK
// BAD: Missing InitAPI/ShutdownAPI
#include <aws/s3/S3Client.h>
void badExample() {
    Aws::S3::S3Client client;  // CRASH: SDK not initialized
    auto outcome = client.ListBuckets();
}

// GOOD: Proper initialization
#include <aws/core/Aws.h>
void goodExample() {
    Aws::SDKOptions options;
    Aws::InitAPI(options);
    {
        Aws::S3::S3Client client;
        auto outcome = client.ListBuckets();
    }
    Aws::ShutdownAPI(options);
}

// PITFALL 2: Not checking outcome success
// BAD: Assuming success
void badUpload(const std::string& bucket, const std::string& key) {
    Aws::S3::S3Client client;
    Aws::S3::Model::PutObjectRequest request;
    request.SetBucket(bucket);
    request.SetKey(key);
    auto outcome = client.PutObject(request);
    std::cout << "ETag: " << outcome.GetResult().GetETag();  // CRASH if failed
}

// GOOD: Check outcome
void goodUpload(const std::string& bucket, const std::string& key) {
    Aws::S3::S3Client client;
    Aws::S3::Model::PutObjectRequest request;
    request.SetBucket(bucket);
    request.SetKey(key);
    auto outcome = client.PutObject(request);
    if (outcome.IsSuccess()) {
        std::cout << "ETag: " << outcome.GetResult().GetETag();
    } else {
        std::cerr << "Error: " << outcome.GetError().GetMessage();
    }
}

// PITFALL 3: Memory leaks with shared pointers
// BAD: Not using custom allocator
void badMemory() {
    auto stream = std::make_shared<std::fstream>("file.txt", std::ios::in);
    // Memory tracked by default allocator, not AWS SDK
}

// GOOD: Use AWS SDK allocator
void goodMemory() {
    auto stream = Aws::MakeShared<Aws::FStream>("MyTag", "file.txt", std::ios::in);
}

// PITFALL 4: Thread safety with client configuration
// BAD: Modifying client config from multiple threads
void badThreading(Aws::S3::S3Client& client) {
    std::thread t1([&]() { client.SetRegion("us-east-1"); });
    std::thread t2([&]() { client.ListBuckets(); });  // Race condition
    t1.join(); t2.join();
}

// GOOD: Configure once, then use read-only
void goodThreading() {
    Aws::Client::ClientConfiguration config;
    config.region = "us-east-1";
    Aws::S3::S3Client client(config);
    // Now safe to use from multiple threads
}

// PITFALL 5: Not handling large objects properly
// BAD: Loading entire object into memory
void badLargeObject(const std::string& bucket, const std::string& key) {
    Aws::S3::S3Client client;
    Aws::S3::Model::GetObjectRequest request;
    request.SetBucket(bucket);
    request.SetKey(key);
    auto outcome = client.GetObject(request);
    auto& body = outcome.GetResultWithOwnership().GetBody();
    std::stringstream ss;
    ss << body.rdbuf();  // Loads entire object into memory
}

// GOOD: Stream processing
void goodLargeObject(const std::string& bucket, const std::string& key) {
    Aws::S3::S3Client client;
    Aws::S3::Model::GetObjectRequest request;
    request.SetBucket(bucket);
    request.SetKey(key);
    auto outcome = client.GetObject(request);
    auto& body = outcome.GetResultWithOwnership().GetBody();
    char buffer[8192];
    while (body.read(buffer, sizeof(buffer)) || body.gcount() > 0) {
        processChunk(buffer, body.gcount());
    }
}

// PITFALL 6: Ignoring retry configuration
// BAD: Default retries may not be sufficient
void badRetry() {
    Aws::S3::S3Client client;  // Default retry strategy
}

// GOOD: Configure retry strategy
void goodRetry() {
    Aws::Client::ClientConfiguration config;
    config.retryStrategy = Aws::MakeShared<Aws::Client::DefaultRetryStrategy>("Retry", 5, 1000);
    Aws::S3::S3Client client(config);
}

// PITFALL 7: Not setting timeouts
// BAD: No timeout configuration
void badTimeout() {
    Aws::S3::S3Client client;
    // Could hang indefinitely on network issues
}

// GOOD: Set appropriate timeouts
void goodTimeout() {
    Aws::Client::ClientConfiguration config;
    config.connectTimeoutMs = 5000;
    config.requestTimeoutMs = 30000;
    Aws::S3::S3Client client(config);
}

// PITFALL 8: Using deprecated APIs
// BAD: Using deprecated methods
void badDeprecated() {
    Aws::S3::S3Client client;
    // Some older API versions have deprecated methods
}

// GOOD: Use current API
void goodCurrent() {
    Aws::S3::S3Client client;
    // Always use the latest API methods
}
```