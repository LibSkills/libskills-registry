# Performance

```cpp
// PERFORMANCE CHARACTERISTICS
// 1. Connection pooling reduces latency
#include <aws/core/http/HttpClientFactory.h>

void configureConnectionPooling() {
    Aws::Client::ClientConfiguration config;
    config.maxConnections = 100;  // Increase for high throughput
    config.enableTcpKeepAlive = true;
    config.tcpKeepAliveIntervalMs = 30000;
    
    Aws::S3::S3Client client(config);
}

// 2. Use async operations for parallel requests
#include <future>
#include <vector>

std::vector<std::future<Aws::S3::Model::GetObjectOutcome>> parallelDownloads(
    Aws::S3::S3Client& client,
    const std::vector<std::pair<std::string, std::string>>& objects) {
    
    std::vector<std::future<Aws::S3::Model::GetObjectOutcome>> futures;
    futures.reserve(objects.size());
    
    for (const auto& [bucket, key] : objects) {
        futures.push_back(std::async(std::launch::async, [&client, bucket, key]() {
            Aws::S3::Model::GetObjectRequest request;
            request.SetBucket(bucket);
            request.SetKey(key);
            return client.GetObject(request);
        }));
    }
    
    return futures;
}

// 3. Memory allocation patterns
// BAD: Frequent allocations
void badAllocationPattern() {
    for (int i = 0; i < 1000; ++i) {
        Aws::S3::S3Client client;  // Expensive: creates new HTTP client each time
        auto outcome = client.ListBuckets();
    }
}

// GOOD: Reuse client
void goodAllocationPattern() {
    Aws::S3::S3Client client;
    for (int i = 0; i < 1000; ++i) {
        auto outcome = client.ListBuckets();
    }
}

// 4. Buffer management for large transfers
class OptimizedTransfer {
    static const size_t BUFFER_SIZE = 64 * 1024;  // 64KB buffer
    
    std::vector<char> buffer;
    
public:
    OptimizedTransfer() : buffer(BUFFER_SIZE) {}
    
    void downloadToFile(Aws::S3::S3Client& client,
                        const std::string& bucket,
                        const std::string& key,
                        const std::string& outputPath) {
        Aws::S3::Model::GetObjectRequest request;
        request.SetBucket(bucket);
        request.SetKey(key);
        
        auto outcome = client.GetObject(request);
        if (!outcome.IsSuccess()) return;
        
        auto& body = outcome.GetResultWithOwnership().GetBody();
        std::ofstream output(outputPath, std::ios::binary);
        
        while (body) {
            body.read(buffer.data(), BUFFER_SIZE);
            output.write(buffer.data(), body.gcount());
        }
    }
};

// 5. Use range requests for partial downloads
void partialDownload(Aws::S3::S3Client& client,
                     const std::string& bucket,
                     const std::string& key,
                     size_t offset,
                     size_t length) {
    Aws::S3::Model::GetObjectRequest request;
    request.SetBucket(bucket);
    request.SetKey(key);
    request.SetRange("bytes=" + std::to_string(offset) + "-" + 
                     std::to_string(offset + length - 1));
    
    auto outcome = client.GetObject(request);
}

// 6. Optimize serialization
// BAD: Default serialization
void badSerialization() {
    Aws::S3::Model::PutObjectRequest request;
    request.SetBucket("my-bucket");
    request.SetKey("my-key");
    // Default serialization may be slow for complex objects
}

// GOOD: Use raw pointers for large payloads
void goodSerialization(const std::string& bucket, const std::string& key,
                       const char* data, size_t size) {
    Aws::S3::Model::PutObjectRequest request;
    request.SetBucket(bucket);
    request.SetKey(key);
    
    auto stream = Aws::MakeShared<Aws::StringStream>("Payload");
    stream->write(data, size);
    request.SetBody(stream);
}

// 7. Batch operations for better throughput
void batchDelete(Aws::S3::S3Client& client,
                 const std::string& bucket,
                 const std::vector<std::string>& keys) {
    Aws::S3::Model::DeleteObjectsRequest request;
    request.SetBucket(bucket);
    
    Aws::S3::Model::Delete deleteObjects;
    for (const auto& key : keys) {
        Aws::S3::Model::ObjectIdentifier identifier;
        identifier.SetKey(key);
        deleteObjects.AddObjects(identifier);
    }
    request.SetDelete(deleteObjects);
    
    auto outcome = client.DeleteObjects(request);
}

// 8. Use transfer manager for large files
#include <aws/transfer/TransferManager.h>

void optimizedLargeTransfer(const std::string& bucket,
                           const std::string& key,
                           const std::string& filePath) {
    Aws::Transfer::TransferManagerConfiguration transferConfig;
    transferConfig.s3Client = Aws::MakeShared<Aws::S3::S3Client>("Transfer");
    
    auto transferManager = Aws::Transfer::TransferManager::Create(transferConfig);
    
    auto transferHandle = transferManager->UploadFile(
        filePath.c_str(),
        bucket.c_str(),
        key.c_str(),
        "text/plain",
        Aws::Map<Aws::String, Aws::String>());
    
    transferHandle->WaitUntilFinished();
}
```