# Threading

```cpp
#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>
#include <mutex>
#include <thread>
#include <vector>

// Thread safety guarantee: RapidJSON documents are NOT thread-safe
// Each document must be protected by external synchronization

// Pattern 1: Mutex-protected document access
class ThreadSafeDocument {
    rapidjson::Document doc_;
    mutable std::mutex mutex_;
    
public:
    void parse(const std::string& json) {
        std::lock_guard<std::mutex> lock(mutex_);
        doc_.Parse(json.c_str());
    }
    
    std::string serialize() const {
        std::lock_guard<std::mutex> lock(mutex_);
        rapidjson::StringBuffer buffer;
        rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
        doc_.Accept(writer);
        return buffer.GetString();
    }
    
    void modify(const std::string& key, const std::string& value) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (!doc_.HasMember(key.c_str())) {
            doc_.AddMember(
                rapidjson::Value(key.c_str(), doc_.GetAllocator()).Move(),
                rapidjson::Value(value.c_str(), doc_.GetAllocator()).Move(),
                doc_.GetAllocator()
            );
        }
    }
};

// Pattern 2: Thread-local documents (no synchronization needed)
void thread_local_documents() {
    auto worker = [](int id) {
        // Each thread gets its own document
        rapidjson::Document doc;
        doc.SetObject();
        doc.AddMember("thread_id", id, doc.GetAllocator());
        
        // No synchronization needed
        rapidjson::StringBuffer buffer;
        rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
        doc.Accept(writer);
        std::cout << "Thread " << id << ": " << buffer.GetString() << std::endl;
    };
    
    std::vector<std::thread> threads;
    for (int i = 0; i < 4; i++) {
        threads.emplace_back(worker, i);
    }
    for (auto& t : threads) t.join();
}

// Pattern 3: Read-write lock for concurrent reads
class ReadWriteDocument {
    rapidjson::Document doc_;
    mutable std::shared_mutex rw_mutex_;
    
public:
    std::string readValue(const std::string& key) const {
        std::shared_lock<std::shared_mutex> lock(rw_mutex_);
        if (doc_.HasMember(key.c_str()) && doc_[key.c_str()].IsString()) {
            return doc_[key.c_str()].GetString();
        }
        return "";
    }
    
    void writeValue(const std::string& key, const std::string& value) {
        std::unique_lock<std::shared_mutex> lock(rw_mutex_);
        if (doc_.HasMember(key.c_str())) {
            doc_[key.c_str()].SetString(value.c_str(), doc_.GetAllocator());
        } else {
            doc_.AddMember(
                rapidjson::Value(key.c_str(), doc_.GetAllocator()).Move(),
                rapidjson::Value(value.c_str(), doc_.GetAllocator()).Move(),
                doc_.GetAllocator()
            );
        }
    }
};

// Pattern 4: Copy-on-write for concurrent access
class CopyOnWriteDocument {
    std::shared_ptr<rapidjson::Document> doc_;
    mutable std::mutex mutex_;
    
public:
    CopyOnWriteDocument() : doc_(std::make_shared<rapidjson::Document>()) {
        doc_->SetObject();
    }
    
    std::shared_ptr<const rapidjson::Document> read() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return doc_; // Atomic shared_ptr copy
    }
    
    void write(std::function<void(rapidjson::Document&)> modifier) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto newDoc = std::make_shared<rapidjson::Document>(*doc_, doc_->GetAllocator());
        modifier(*newDoc);
        doc_ = newDoc; // Atomic swap
    }
};

// Pattern 5: Thread-safe allocator (NOT recommended)
void thread_safe_allocator_warning() {
    // WARNING: RapidJSON allocators are NOT thread-safe
    // Do NOT share allocators between threads
    
    // BAD: Shared allocator
    rapidjson::MemoryPoolAllocator<> sharedAlloc;
    // Thread 1: doc1 uses sharedAlloc
    // Thread 2: doc2 uses sharedAlloc  // RACE CONDITION!
    
    // GOOD: Separate allocators per thread
    auto worker = []() {
        rapidjson::MemoryPoolAllocator<> localAlloc;
        rapidjson::Document doc(&localAlloc);
        // Safe to use doc in this thread
    };
}

// Pattern 6: Producer-consumer with JSON documents
void producer_consumer() {
    std::mutex queue_mutex;
    std::vector<rapidjson::Document> queue;
    
    auto producer = [&]() {
        rapidjson::Document doc;
        doc.SetObject();
        doc.AddMember("data", "produced", doc.GetAllocator());
        
        std::lock_guard<std::mutex> lock(queue_mutex);
        queue.push_back(std::move(doc)); // Move into queue
    };
    
    auto consumer = [&]() {
        rapidjson::Document doc;
        {
            std::lock_guard<std::mutex> lock(queue_mutex);
            if (!queue.empty()) {
                doc = std::move(queue.back()); // Move out of queue
                queue.pop_back();
            }
        }
        // Process doc
    };
}
```