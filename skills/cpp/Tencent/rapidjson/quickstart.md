# Quickstart

```cpp
#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>
#include <iostream>

// Pattern 1: Parse JSON from string
void parse_json() {
    const char* json = R"({"name":"John","age":30,"city":"New York"})";
    rapidjson::Document doc;
    doc.Parse(json);
    
    if (doc.HasParseError()) {
        std::cerr << "Parse error: " << doc.GetParseError() << std::endl;
        return;
    }
    
    std::cout << doc["name"].GetString() << std::endl; // John
}

// Pattern 2: Access nested objects
void access_nested() {
    const char* json = R"({"person":{"name":"Alice","address":{"city":"NYC"}}})";
    rapidjson::Document doc;
    doc.Parse(json);
    
    if (doc["person"].IsObject() && doc["person"].HasMember("address")) {
        const auto& addr = doc["person"]["address"];
        if (addr.IsObject() && addr.HasMember("city")) {
            std::cout << addr["city"].GetString() << std::endl; // NYC
        }
    }
}

// Pattern 3: Create JSON document
void create_json() {
    rapidjson::Document doc;
    doc.SetObject();
    
    rapidjson::Document::AllocatorType& alloc = doc.GetAllocator();
    
    doc.AddMember("name", "Bob", alloc);
    doc.AddMember("age", 25, alloc);
    
    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
    doc.Accept(writer);
    
    std::cout << buffer.GetString() << std::endl; // {"name":"Bob","age":25}
}

// Pattern 4: Iterate over arrays
void iterate_array() {
    const char* json = R"({"items":[1,2,3,4,5]})";
    rapidjson::Document doc;
    doc.Parse(json);
    
    if (doc["items"].IsArray()) {
        for (auto& v : doc["items"].GetArray()) {
            std::cout << v.GetInt() << " ";
        }
    }
}

// Pattern 5: Modify existing JSON
void modify_json() {
    const char* json = R"({"name":"Charlie","age":30})";
    rapidjson::Document doc;
    doc.Parse(json);
    
    rapidjson::Document::AllocatorType& alloc = doc.GetAllocator();
    
    // Add new field
    doc.AddMember("city", "London", alloc);
    
    // Modify existing field
    doc["age"].SetInt(31);
}

// Pattern 6: Pretty print JSON
void pretty_print() {
    rapidjson::Document doc;
    doc.Parse(R"({"name":"Dave","age":40})");
    
    rapidjson::StringBuffer buffer;
    rapidjson::PrettyWriter<rapidjson::StringBuffer> writer(buffer);
    doc.Accept(writer);
    
    std::cout << buffer.GetString() << std::endl;
}

// Pattern 7: Read from file
#include <fstream>
void read_from_file(const std::string& filename) {
    std::ifstream file(filename);
    std::string content((std::istreambuf_iterator<char>(file)), 
                        std::istreambuf_iterator<char>());
    
    rapidjson::Document doc;
    doc.Parse(content.c_str());
}

// Pattern 8: Write to file
void write_to_file(const std::string& filename) {
    rapidjson::Document doc;
    doc.SetObject();
    doc.AddMember("key", "value", doc.GetAllocator());
    
    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
    doc.Accept(writer);
    
    std::ofstream file(filename);
    file << buffer.GetString();
}
```