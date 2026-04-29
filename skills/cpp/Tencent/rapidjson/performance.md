# Performance

```cpp
#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>
#include <rapidjson/reader.h>
#include <chrono>
#include <iostream>

// Performance characteristic 1: In-situ vs non-insitu parsing
void parsing_performance() {
    std::string json = R"({"data":"very long string value that would be copied"})";
    
    // In-situ: ~2x faster, modifies input string
    rapidjson::Document doc1;
    doc1.ParseInsitu(&json[0]); // No string copying
    
    // Non-insitu: copies strings
    rapidjson::Document doc2;
    doc2.Parse(json.c_str()); // Copies all strings
}

// Performance characteristic 2: SAX vs DOM parsing
void sax_vs_dom() {
    const char* json = R"([1,2,3,4,5,6,7,8,9,10])";
    
    // DOM: Loads entire document into memory
    rapidjson::Document doc;
    doc.Parse(json);
    int sum = 0;
    for (auto& v : doc.GetArray()) {
        sum += v.GetInt();
    }
    
    // SAX: Stream processing, lower memory
    struct SumHandler : public rapidjson::BaseReaderHandler<> {
        int sum = 0;
        bool Int(int i) override { sum += i; return true; }
    };
    
    SumHandler handler;
    rapidjson::Reader reader;
    rapidjson::StringStream ss(json);
    reader.Parse(ss, handler);
}

// Performance characteristic 3: Allocator strategies
void allocator_performance() {
    // Default allocator (good for most cases)
    rapidjson::Document doc1;
    
    // Stack allocator (fast for small documents)
    char buffer[4096];
    rapidjson::MemoryPoolAllocator<> stackAlloc(buffer, sizeof(buffer));
    rapidjson::Document doc2(&stackAlloc);
    
    // Pre-allocated allocator (best for known sizes)
    rapidjson::MemoryPoolAllocator<> preAlloc(1024 * 1024); // 1MB pool
    rapidjson::Document doc3(&preAlloc);
}

// Performance tip 1: Reserve space
void reserve_space() {
    rapidjson::Document doc;
    doc.SetObject();
    
    // Pre-allocate member capacity
    doc.MemberReserve(1000, doc.GetAllocator());
    
    // Pre-allocate array capacity
    rapidjson::Value arr(rapidjson::kArrayType);
    arr.Reserve(1000, doc.GetAllocator());
}

// Performance tip 2: Use raw strings for known values
void raw_strings() {
    rapidjson::Document doc;
    doc.SetObject();
    
    // Slow: Allocates and copies
    doc.AddMember("key", "value", doc.GetAllocator());
    
    // Fast: No allocation for string literals
    rapidjson::Value val;
    val.SetString("value"); // StringRef, no copy
    doc.AddMember("key", val, doc.GetAllocator());
}

// Performance tip 3: Batch operations
void batch_operations() {
    rapidjson::Document doc;
    doc.SetObject();
    auto& alloc = doc.GetAllocator();
    
    // Slow: Multiple allocations
    for (int i = 0; i < 1000; i++) {
        doc.AddMember("key", i, alloc);
    }
    
    // Fast: Single allocation with reserve
    doc.MemberReserve(1000, alloc);
    for (int i = 0; i < 1000; i++) {
        doc.AddMember("key", i, alloc);
    }
}

// Performance tip 4: Avoid unnecessary deep copies
void avoid_copies() {
    rapidjson::Document source;
    source.Parse(json_string);
    
    // Bad: Deep copy entire document
    rapidjson::Document copy(source, source.GetAllocator());
    
    // Good: Move if source not needed
    rapidjson::Document moved(std::move(source));
    
    // Good: Reference if read-only
    const rapidjson::Document& ref = source;
}
```