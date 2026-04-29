# Best Practices

```cpp
// BEST PRACTICE 1: Use a singleton SDK manager
#include <aws/core/Aws.h>
#include <mutex>

class AWSSDKManager {
    Aws::SDKOptions options;
    std::mutex mutex;
    int refCount = 0;
    
public:
    void initialize() {
        std::lock_guard<std::mutex> lock(mutex);
        if (refCount++ == 0) {
            Aws::InitAPI(options);
        }
    }
    
    void shutdown() {
        std::lock_guard<std::mutex> lock(mutex);
        if (--refCount == 0) {
            Aws::ShutdownAPI(options);
        }
    }
};

// BEST PRACTICE 2: Create reusable client factory
class S3ClientFactory {
    Aws::Client::ClientConfiguration config;
    
public:
    S3ClientFactory() {
        config.region = Aws::Environment::GetEnv("AWS_DEFAULT_REGION").c_str();
        config.connectTimeoutMs = 5000;
        config.requestTimeoutMs = 30000;
        config.retryStrategy = Aws::MakeShared<Aws::Client::DefaultRetryStrategy>(
            "Retry", 3, 1000);
    }
    
    Aws::S3::S3Client createClient() {
        return Aws::S3::S3Client(config);
    }
};

// BEST PRACTICE 3: Use async operations for better throughput
#include <future>
#include <aws/s3/model/GetObjectRequest.h>

std::future<Aws::S3::Model::GetObjectOutcome> asyncGetObject(
    Aws::S3::S3Client& client,
    const std::string& bucket,
    const std::string& key) {
    
    return std::async(std::launch::async, [&client, bucket, key]() {
        Aws::S3::Model::GetObjectRequest request;
        request.SetBucket(bucket);
        request.SetKey(key);
        return client.GetObject(request);
    });
}

// BEST PRACTICE 4: Implement proper error handling with retries
class S3Operation {
    Aws::S3::S3Client& client;
    int maxRetries = 3;
    
public:
    template<typename Request, typename Operation>
    auto executeWithRetry(Request request, Operation op) -> decltype(op(request)) {
        for (int attempt = 0; attempt < maxRetries; ++attempt) {
            auto outcome = op(request);
            if (outcome.IsSuccess()) {
                return outcome;
            }
            
            auto error = outcome.GetError();
            if (error.GetErrorType() != Aws::S3::S3Errors::SLOW_DOWN &&
                error.GetErrorType() != Aws::S3::S3Errors::INTERNAL_FAILURE) {
                return outcome;  // Non-retryable error
            }
            
            std::this_thread::sleep_for(std::chrono::milliseconds(100 * (attempt + 1)));
        }
        return op(request);  // Final attempt
    }
};

// BEST PRACTICE 5: Use connection pooling
#include <aws/core/http/HttpClientFactory.h>

void configureConnectionPool() {
    Aws::Client::ClientConfiguration config;
    config.maxConnections = 25;  // Increase from default 25
    config.enableTcpKeepAlive = true;
    config.tcpKeepAliveIntervalMs = 30000;
    
    Aws::S3::S3Client client(config);
}

// BEST PRACTICE 6: Implement request tracing for debugging
#include <aws/core/utils/logging/LogLevel.h>

void enableLogging() {
    Aws::Utils::Logging::InitializeAWSLogging(
        Aws::MakeShared<Aws::Utils::Logging::DefaultLogSystem>(
            "Logging", Aws::Utils::Logging::LogLevel::Info, "aws_sdk.log"));
}

// BEST PRACTICE 7: Use multipart upload for large files
#include <aws/s3/model/CreateMultipartUploadRequest.h>
#include <aws/s3/model/UploadPartRequest.h>
#include <aws/s3/model/CompleteMultipartUploadRequest.h>

void multipartUpload(const std::string& bucket, const std::string& key, 
                     const std::string& filePath) {
    Aws::S3::S3Client client;
    
    // Initiate multipart upload
    Aws::S3::Model::CreateMultipartUploadRequest createRequest;
    createRequest.SetBucket(bucket);
    createRequest.SetKey(key);
    auto createOutcome = client.CreateMultipartUpload(createRequest);
    
    if (!createOutcome.IsSuccess()) {
        throw std::runtime_error("Failed to initiate multipart upload");
    }
    
    auto uploadId = createOutcome.GetResult().GetUploadId();
    std::vector<Aws::String> partETags;
    
    // Upload parts
    const size_t partSize = 5 * 1024 * 1024; // 5MB
    std::ifstream file(filePath, std::ios::binary);
    int partNumber = 1;
    
    while (file) {
        std::vector<char> buffer(partSize);
        file.read(buffer.data(), partSize);
        auto bytesRead = file.gcount();
        
        if (bytesRead > 0) {
            Aws::S3::Model::UploadPartRequest uploadRequest;
            uploadRequest.SetBucket(bucket);
            uploadRequest.SetKey(key);
            uploadRequest.SetUploadId(uploadId);
            uploadRequest.SetPartNumber(partNumber);
            
            auto stream = Aws::MakeShared<Aws::StringStream>("PartData");
            stream->write(buffer.data(), bytesRead);
            uploadRequest.SetBody(stream);
            
            auto uploadOutcome = client.UploadPart(uploadRequest);
            if (uploadOutcome.IsSuccess()) {
                partETags.push_back(uploadOutcome.GetResult().GetETag());
            }
            ++partNumber;
        }
    }
    
    // Complete multipart upload
    Aws::S3::Model::CompleteMultipartUploadRequest completeRequest;
    completeRequest.SetBucket(bucket);
    completeRequest.SetKey(key);
    completeRequest.SetUploadId(uploadId);
    
    Aws::S3::Model::CompletedMultipartUpload completedUpload;
    for (size_t i = 0; i < partETags.size(); ++i) {
        Aws::S3::Model::CompletedPart completedPart;
        completedPart.SetPartNumber(static_cast<int>(i + 1));
        completedPart.SetETag(partETags[i]);
        completedUpload.AddParts(completedPart);
    }
    completeRequest.SetMultipartUpload(completedUpload);
    
    auto completeOutcome = client.CompleteMultipartUpload(completeRequest);
    if (!completeOutcome.IsSuccess()) {
        throw std::runtime_error("Failed to complete multipart upload");
    }
}
```