# Lifecycle

```cpp
#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>
#include <iostream>

// Construction: Default and with allocator
void construction_examples() {
    // Default construction (uses default allocator)
    rapidjson::Document doc1;
    
    // Construction with custom allocator
    rapidjson::MemoryPoolAllocator<> customAlloc;
    rapidjson::Document doc2(&customAlloc);
    
    // Construction from parsed JSON
    rapidjson::Document doc3;
    doc3.Parse(R"({"key":"value"})");
    
    // Copy construction (deep copy)
    rapidjson::Document doc4(doc3, doc3.GetAllocator());
}

// Destruction: Automatic cleanup
void destruction_examples() {
    {
        rapidjson::Document doc;
        doc.SetObject();
        doc.AddMember("data", "temporary", doc.GetAllocator());
        // doc automatically cleaned up when scope exits
    }
    
    // Manual cleanup (rarely needed)
    rapidjson::Document doc;
    doc.SetObject();
    doc.AddMember("data", "value", doc.GetAllocator());
    doc.Clear(); // Clears all members, but keeps allocator
}

// Move semantics
void move_semantics() {
    rapidjson::Document source;
    source.SetObject();
    source.AddMember("key", "value", source.GetAllocator());
    
    // Move document (source becomes empty/null)
    rapidjson::Document dest(std::move(source));
    // source is now null
    std::cout << source.IsNull() << std::endl; // true
    
    // Move assignment
    rapidjson::Document another;
    another = std::move(dest);
}

// Resource management with custom allocator
void resource_management() {
    // Stack allocator for small documents
    char buffer[1024];
    rapidjson::MemoryPoolAllocator<rapidjson::CrtAllocator> stackAlloc(buffer, sizeof(buffer));
    rapidjson::Document doc(&stackAlloc);
    
    // CRT allocator for large documents
    rapidjson::CrtAllocator crtAlloc;
    rapidjson::Document largeDoc(&crtAlloc);
    
    // Custom allocator with pooling
    class PoolAllocator : public rapidjson::Allocator {
        // Implement custom allocation strategy
    };
}

// Value lifecycle
void value_lifecycle() {
    rapidjson::Document doc;
    rapidjson::Document::AllocatorType& alloc = doc.GetAllocator();
    
    // Creating values
    rapidjson::Value stringVal;
    stringVal.SetString("hello", alloc); // String is copied to allocator
    
    rapidjson::Value objectVal(rapidjson::kObjectType);
    objectVal.AddMember("key", stringVal, alloc); // stringVal is moved
    
    // Value ownership
    rapidjson::Value ownedValue;
    ownedValue.SetString("owned", alloc); // Owns its string data
    
    // Moving values between documents
    rapidjson::Document doc2;
    rapidjson::Value movedValue;
    movedValue.SetString("moved", alloc);
    doc2.AddMember("item", movedValue, doc2.GetAllocator()); // Error: wrong allocator
    
    // Correct way to move between documents
    rapidjson::Value copiedValue(movedValue, doc2.GetAllocator()); // Deep copy
    doc2.AddMember("item", copiedValue, doc2.GetAllocator());
}
```