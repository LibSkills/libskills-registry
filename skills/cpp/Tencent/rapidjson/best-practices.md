# Best Practices

```cpp
#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>
#include <rapidjson/error/en.h>
#include <stdexcept>
#include <optional>

// Best Practice 1: Create a safe parsing wrapper
class SafeJsonParser {
public:
    static rapidjson::Document parse(const std::string& json) {
        rapidjson::Document doc;
        doc.Parse(json.c_str());
        
        if (doc.HasParseError()) {
            throw std::runtime_error(
                std::string("JSON parse error: ") + 
                rapidjson::GetParseError_En(doc.GetParseError()) +
                " at offset " + std::to_string(doc.GetErrorOffset())
            );
        }
        return doc;
    }
};

// Best Practice 2: Type-safe accessor functions
template<typename T>
std::optional<T> getValue(const rapidjson::Value& obj, const char* key);

template<>
std::optional<int> getValue<int>(const rapidjson::Value& obj, const char* key) {
    if (obj.HasMember(key) && obj[key].IsInt()) {
        return obj[key].GetInt();
    }
    return std::nullopt;
}

template<>
std::optional<std::string> getValue<std::string>(const rapidjson::Value& obj, const char* key) {
    if (obj.HasMember(key) && obj[key].IsString()) {
        return obj[key].GetString();
    }
    return std::nullopt;
}

// Best Practice 3: Use RAII for JSON file handling
class JsonFile {
    rapidjson::Document doc_;
    std::string filename_;
    
public:
    JsonFile(const std::string& filename) : filename_(filename) {
        std::ifstream file(filename);
        if (!file.is_open()) {
            throw std::runtime_error("Cannot open file: " + filename);
        }
        std::string content((std::istreambuf_iterator<char>(file)), 
                           std::istreambuf_iterator<char>());
        doc_ = SafeJsonParser::parse(content);
    }
    
    void save() const {
        rapidjson::StringBuffer buffer;
        rapidjson::PrettyWriter<rapidjson::StringBuffer> writer(buffer);
        doc_.Accept(writer);
        
        std::ofstream file(filename_);
        file << buffer.GetString();
    }
    
    rapidjson::Document& getDocument() { return doc_; }
};

// Best Practice 4: Pre-allocate memory for large documents
void process_large_json() {
    rapidjson::Document doc;
    doc.Parse(json_string);
    
    // Reserve space for known structure
    if (doc.IsObject()) {
        doc.MemberReserve(100, doc.GetAllocator()); // Pre-allocate for 100 members
    }
}

// Best Practice 5: Use move semantics for efficiency
rapidjson::Document create_document() {
    rapidjson::Document doc;
    doc.SetObject();
    doc.AddMember("type", "config", doc.GetAllocator());
    return doc; // Move semantics, no copy
}

// Best Practice 6: Validate JSON structure with schema-like checks
class JsonValidator {
public:
    static void validateUser(const rapidjson::Value& user) {
        if (!user.IsObject()) throw std::runtime_error("User must be an object");
        
        auto name = getValue<std::string>(user, "name");
        if (!name || name->empty()) throw std::runtime_error("User must have non-empty name");
        
        auto age = getValue<int>(user, "age");
        if (!age || *age < 0 || *age > 150) throw std::runtime_error("Invalid age");
    }
};
```