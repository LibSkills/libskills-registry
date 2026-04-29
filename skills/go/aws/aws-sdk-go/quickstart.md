# Quickstart

```cpp
// Basic S3 operations with AWS SDK for C++
#include <aws/core/Aws.h>
#include <aws/s3/S3Client.h>
#include <aws/s3/model/ListObjectsRequest.h>
#include <aws/s3/model/GetObjectRequest.h>
#include <aws/s3/model/PutObjectRequest.h>
#include <fstream>
#include <iostream>

// Pattern 1: Initialize SDK and list buckets
void listBuckets() {
    Aws::SDKOptions options;
    Aws::InitAPI(options);
    {
        Aws::S3::S3Client client;
        auto outcome = client.ListBuckets();
        if (outcome.IsSuccess()) {
            for (const auto& bucket : outcome.GetResult().GetBuckets()) {
                std::cout << bucket.GetName() << std::endl;
            }
        }
    }
    Aws::ShutdownAPI(options);
}

// Pattern 2: Upload a file to S3
void uploadFile(const std::string& bucket, const std::string& key, const std::string& filePath) {
    Aws::SDKOptions options;
    Aws::InitAPI(options);
    {
        Aws::S3::S3Client client;
        Aws::S3::Model::PutObjectRequest request;
        request.SetBucket(bucket);
        request.SetKey(key);
        
        auto inputData = Aws::MakeShared<Aws::FStream>("upload", filePath.c_str(), std::ios::binary | std::ios::in);
        request.SetBody(inputData);
        
        auto outcome = client.PutObject(request);
        if (outcome.IsSuccess()) {
            std::cout << "Upload successful" << std::endl;
        }
    }
    Aws::ShutdownAPI(options);
}

// Pattern 3: Download a file from S3
void downloadFile(const std::string& bucket, const std::string& key, const std::string& outputPath) {
    Aws::SDKOptions options;
    Aws::InitAPI(options);
    {
        Aws::S3::S3Client client;
        Aws::S3::Model::GetObjectRequest request;
        request.SetBucket(bucket);
        request.SetKey(key);
        
        auto outcome = client.GetObject(request);
        if (outcome.IsSuccess()) {
            auto& result = outcome.GetResultWithOwnership();
            Aws::OFStream outputFile(outputPath, std::ios::binary);
            outputFile << result.GetBody().rdbuf();
        }
    }
    Aws::ShutdownAPI(options);
}

// Pattern 4: List objects in a bucket
void listObjects(const std::string& bucket) {
    Aws::SDKOptions options;
    Aws::InitAPI(options);
    {
        Aws::S3::S3Client client;
        Aws::S3::Model::ListObjectsRequest request;
        request.SetBucket(bucket);
        
        auto outcome = client.ListObjects(request);
        if (outcome.IsSuccess()) {
            for (const auto& obj : outcome.GetResult().GetContents()) {
                std::cout << obj.GetKey() << " (" << obj.GetSize() << " bytes)" << std::endl;
            }
        }
    }
    Aws::ShutdownAPI(options);
}

// Pattern 5: Delete an object
void deleteObject(const std::string& bucket, const std::string& key) {
    Aws::SDKOptions options;
    Aws::InitAPI(options);
    {
        Aws::S3::S3Client client;
        Aws::S3::Model::DeleteObjectRequest request;
        request.SetBucket(bucket);
        request.SetKey(key);
        
        auto outcome = client.DeleteObject(request);
        if (outcome.IsSuccess()) {
            std::cout << "Object deleted" << std::endl;
        }
    }
    Aws::ShutdownAPI(options);
}

// Pattern 6: Check if object exists
bool objectExists(const std::string& bucket, const std::string& key) {
    Aws::SDKOptions options;
    Aws::InitAPI(options);
    bool exists = false;
    {
        Aws::S3::S3Client client;
        Aws::S3::Model::HeadObjectRequest request;
        request.SetBucket(bucket);
        request.SetKey(key);
        
        auto outcome = client.HeadObject(request);
        exists = outcome.IsSuccess();
    }
    Aws::ShutdownAPI(options);
    return exists;
}

// Pattern 7: Copy object between buckets
void copyObject(const std::string& sourceBucket, const std::string& sourceKey,
                const std::string& destBucket, const std::string& destKey) {
    Aws::SDKOptions options;
    Aws::InitAPI(options);
    {
        Aws::S3::S3Client client;
        Aws::S3::Model::CopyObjectRequest request;
        request.SetCopySource(sourceBucket + "/" + sourceKey);
        request.SetBucket(destBucket);
        request.SetKey(destKey);
        
        auto outcome = client.CopyObject(request);
        if (outcome.IsSuccess()) {
            std::cout << "Copy successful" << std::endl;
        }
    }
    Aws::ShutdownAPI(options);
}

// Pattern 8: Generate presigned URL
#include <aws/s3/model/PutObjectRequest.h>
#include <aws/core/auth/AWSCredentialsProviderChain.h>

std::string generatePresignedUrl(const std::string& bucket, const std::string& key, int expirationSeconds) {
    Aws::SDKOptions options;
    Aws::InitAPI(options);
    std::string url;
    {
        Aws::S3::S3Client client;
        Aws::S3::Model::PutObjectRequest request;
        request.SetBucket(bucket);
        request.SetKey(key);
        
        Aws::String presignedUrl = client.GeneratePresignedUrl(request, expirationSeconds);
        url = presignedUrl.c_str();
    }
    Aws::ShutdownAPI(options);
    return url;
}
```