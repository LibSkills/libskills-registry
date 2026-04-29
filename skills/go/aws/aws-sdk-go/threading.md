# Threading

```cpp
// THREAD SAFETY GUARANTEES
// 1. Client objects are thread-safe for read operations
#include <aws/core/Aws.h>
#include <aws/s3/S3Client.h>
#include <thread>
#include <vector>

class ThreadSafeReader {
    Aws::S3::S3Client client;
    
public:
    ThreadSafeReader() : client() {}
    
    void parallelReads(const std::vector<std::string>& keys) {
        std::vector<std::thread> threads;
        threads.reserve(keys.size());
        
        for (const auto& key : keys) {
            threads.emplace_back([this, key]() {
                Aws::S3::Model::GetObjectRequest request;
                request.SetBucket("my-bucket");
                request.SetKey(key);
                auto outcome = client.GetObject(request);  // Thread-safe
            });
        }
        
        for (auto& t : threads) {
            t.join();
        }
    }
};

// 2. Client configuration is NOT thread-safe after construction
// BAD: Modifying config from multiple threads
void unsafeConfigModification() {
    Aws::S3::S3Client client;
    
    std::thread t1([&client]() {
        client.SetRegion("us-east-1");  // Unsafe
    });
    
    std::thread t2([&client]() {
        client.SetRegion("us-west-2");  // Unsafe
    });
    
    t1.join();
    t2.join();
}

// GOOD: Configure once, then use read-only
void safeConfigUsage() {
    Aws::Client::ClientConfiguration config;
    config.region = "us-east-1";
    Aws::S3::S3Client client(config);  // Configure at construction
    
    std::thread t1([&client]() {
        client.ListBuckets();  // Safe: read-only operation
    });
    
    std::thread t2([&client]() {
        client.ListBuckets();  // Safe: read-only operation
    });
    
    t1.join();
    t2.join();
}

// 3. Shared client with proper synchronization
class SharedClientManager {
    std::shared_ptr<Aws::S3::S3Client> client;
    std::mutex mutex;
    
public:
    SharedClientManager() {
        Aws::Client::ClientConfiguration config;
        config.region = "us-west-2";
        client = std::make_shared<Aws::S3::S3Client>(config);
    }
    
    std::shared_ptr<Aws::S3::S3Client> getClient() {
        return client;  // Safe: shared_ptr is thread-safe
    }
    
    void reconfigure(const std::string& region) {
        std::lock_guard<std::mutex> lock(mutex);
        Aws::Client::ClientConfiguration config;
        config.region = region;
        client = std::make_shared<Aws::S3::S3Client>(config);
    }
};

// 4. Thread-local clients for maximum performance
class ThreadLocalClient {
    thread_local static Aws::S3::S3Client client;
    
public:
    static Aws::S3::S3Client& getClient() {
        return client;
    }
};

// 5. Async operations with proper synchronization
#include <future>
#include <atomic>

class AsyncS3Service {
    Aws::S3::S3Client client;
    std::atomic<int> activeOperations{0};
    
public:
    std::future<Aws::S3::Model::ListBucketsOutcome> listBucketsAsync() {
        activeOperations++;
        return std::async(std::launch::async, [this]() {
            auto outcome = client.ListBuckets();
            activeOperations--;
            return outcome;
        });
    }
    
    void waitForAll() {
        while (activeOperations > 0) {
            std::this_thread::yield();
        }
    }
};

// 6. Thread-safe credential provider
#include <aws/core/auth/AWSCredentialsProviderChain.h>

class ThreadSafeCredentialProvider {
    std::shared_ptr<Aws::Auth::AWSCredentialsProvider> provider;
    std::mutex mutex;
    
public:
    ThreadSafeCredentialProvider() {
        provider = Aws::MakeShared<Aws::Auth::DefaultAWSCredentialsProviderChain>(
            "Credentials");
    }
    
    Aws::Auth::AWSCredentials getCredentials() {
        std::lock_guard<std::mutex> lock(mutex);
        return provider->GetAWSCredentials();  // Thread-safe with mutex
    }
};

// 7. Concurrent operations with different clients
void concurrentOperations() {
    Aws::S3::S3Client client1;
    Aws::S3::S3Client client2;  // Separate client for separate thread
    
    std::thread t1([&client1]() {
        client1.ListBuckets();
    });
    
    std::thread t2([&client2]() {
        client2.ListBuckets();
    });
    
    t1.join();
    t2.join();
}

// 8. Thread-safe error handling
class ThreadSafeErrorHandler {
    std::mutex mutex;
    std::vector<std::string> errors;
    
public:
    void logError(const Aws::S3::S3Error& error) {
        std::lock_guard<std::mutex> lock(mutex);
        errors.push_back(error.GetMessage().c_str());
    }
    
    std::vector<std::string> getErrors() {
        std::lock_guard<std::mutex> lock(mutex);
        return errors;
    }
};
```