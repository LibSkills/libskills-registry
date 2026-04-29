# Lifecycle

```cpp
// CONSTRUCTION: Proper initialization sequence
#include <aws/core/Aws.h>
#include <aws/s3/S3Client.h>

class S3Service {
    Aws::SDKOptions options;
    std::unique_ptr<Aws::S3::S3Client> client;
    
public:
    S3Service() {
        // Step 1: Initialize SDK
        Aws::InitAPI(options);
        
        // Step 2: Configure client
        Aws::Client::ClientConfiguration config;
        config.region = "us-east-1";
        config.connectTimeoutMs = 5000;
        
        // Step 3: Create client
        client = std::make_unique<Aws::S3::S3Client>(config);
    }
    
    // DESTRUCTION: Proper cleanup
    ~S3Service() {
        // Step 1: Destroy client first
        client.reset();
        
        // Step 2: Shutdown SDK
        Aws::ShutdownAPI(options);
    }
    
    // MOVE CONSTRUCTOR
    S3Service(S3Service&& other) noexcept
        : options(std::move(other.options))
        , client(std::move(other.client)) {
        // Reset other to prevent double shutdown
        other.client = nullptr;
    }
    
    // MOVE ASSIGNMENT
    S3Service& operator=(S3Service&& other) noexcept {
        if (this != &other) {
            // Clean up current state
            client.reset();
            Aws::ShutdownAPI(options);
            
            // Move resources
            options = std::move(other.options);
            client = std::move(other.client);
            
            // Reset other
            other.client = nullptr;
        }
        return *this;
    }
    
    // COPY operations are deleted (SDK doesn't support copying clients)
    S3Service(const S3Service&) = delete;
    S3Service& operator=(const S3Service&) = delete;
};

// RESOURCE MANAGEMENT: Proper stream handling
class S3StreamManager {
    Aws::S3::S3Client client;
    
public:
    // Properly manage stream lifecycle
    void uploadStream(const std::string& bucket, const std::string& key,
                      std::istream& data) {
        Aws::S3::Model::PutObjectRequest request;
        request.SetBucket(bucket);
        request.SetKey(key);
        
        // Create a copy of the stream data
        auto stream = Aws::MakeShared<Aws::StringStream>("UploadStream");
        *stream << data.rdbuf();
        request.SetBody(stream);
        
        auto outcome = client.PutObject(request);
        // Stream is automatically cleaned up when shared_ptr goes out of scope
    }
    
    // Download with proper resource cleanup
    std::string downloadToString(const std::string& bucket, const std::string& key) {
        Aws::S3::Model::GetObjectRequest request;
        request.SetBucket(bucket);
        request.SetKey(key);
        
        auto outcome = client.GetObject(request);
        if (!outcome.IsSuccess()) {
            return "";
        }
        
        // GetResultWithOwnership() transfers ownership
        auto& result = outcome.GetResultWithOwnership();
        auto& body = result.GetBody();
        
        std::stringstream ss;
        ss << body.rdbuf();
        return ss.str();
    }
};

// LIFECYCLE WITH SHARED POINTERS
class SharedS3Client {
    std::shared_ptr<Aws::S3::S3Client> client;
    
public:
    SharedS3Client() {
        Aws::Client::ClientConfiguration config;
        config.region = "us-west-2";
        client = Aws::MakeShared<Aws::S3::S3Client>("S3Client", config);
    }
    
    std::shared_ptr<Aws::S3::S3Client> getClient() {
        return client;  // Safe to share
    }
};

// RESOURCE POOLING
class S3ClientPool {
    std::vector<std::unique_ptr<Aws::S3::S3Client>> pool;
    std::mutex mutex;
    
public:
    S3ClientPool(size_t size) {
        Aws::Client::ClientConfiguration config;
        config.maxConnections = static_cast<uint32_t>(size);
        
        for (size_t i = 0; i < size; ++i) {
            pool.push_back(std::make_unique<Aws::S3::S3Client>(config));
        }
    }
    
    std::unique_ptr<Aws::S3::S3Client> acquire() {
        std::lock_guard<std::mutex> lock(mutex);
        if (pool.empty()) return nullptr;
        
        auto client = std::move(pool.back());
        pool.pop_back();
        return client;
    }
    
    void release(std::unique_ptr<Aws::S3::S3Client> client) {
        std::lock_guard<std::mutex> lock(mutex);
        pool.push_back(std::move(client));
    }
};
```