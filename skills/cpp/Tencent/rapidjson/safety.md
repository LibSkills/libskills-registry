# Safety

```cpp
// RED LINE 1: NEVER use in-situ parsing with temporary strings
// BAD: String destroyed before document
std::string get_data() { return "{\"key\":\"value\"}"; }
void unsafe() {
    rapidjson::Document doc;
    std::string data = get_data();
    doc.ParseInsitu(&data[0]); // DANGER: doc references data's buffer
    // If data goes out of scope, doc has dangling pointer
}

// GOOD: Ensure string lifetime or use non-insitu
void safe() {
    std::string data = get_data();
    rapidjson::Document doc;
    doc.Parse(data.c_str()); // Safe: makes internal copy
}

// RED LINE 2: NEVER access members without checking existence
// BAD: Direct access
int val = doc["nonexistent"].GetInt(); // CRASH

// GOOD: Always check
if (doc.HasMember("nonexistent") && doc["nonexistent"].IsInt()) {
    int val = doc["nonexistent"].GetInt();
}

// RED LINE 3: NEVER use references after document modification
// BAD: Reference invalidated
auto& ref = doc["items"];
doc.AddMember("new", 1, doc.GetAllocator()); // May invalidate ref
ref.GetArray(); // UNDEFINED BEHAVIOR

// GOOD: Re-acquire reference
doc.AddMember("new", 1, doc.GetAllocator());
auto& ref = doc["items"];

// RED LINE 4: NEVER mix allocators between documents
// BAD: Using wrong allocator
rapidjson::Document doc1, doc2;
rapidjson::Value val;
val.SetString("test", doc1.GetAllocator());
doc2.AddMember("key", val, doc2.GetAllocator()); // DANGER: val uses doc1's allocator

// GOOD: Use consistent allocator
rapidjson::Value val;
val.SetString("test", doc2.GetAllocator());
doc2.AddMember("key", val, doc2.GetAllocator());

// RED LINE 5: NEVER assume JSON structure without validation
// BAD: No validation
void process_user(const char* json) {
    rapidjson::Document doc;
    doc.Parse(json);
    std::string name = doc["name"].GetString(); // CRASH if not string
    int age = doc["age"].GetInt(); // CRASH if not int
}

// GOOD: Validate structure
void process_user_safe(const char* json) {
    rapidjson::Document doc;
    doc.Parse(json);
    if (doc.HasParseError()) throw std::runtime_error("Invalid JSON");
    if (!doc.IsObject()) throw std::runtime_error("Expected object");
    if (!doc.HasMember("name") || !doc["name"].IsString()) throw std::runtime_error("Invalid name");
    if (!doc.HasMember("age") || !doc["age"].IsInt()) throw std::runtime_error("Invalid age");
    
    std::string name = doc["name"].GetString();
    int age = doc["age"].GetInt();
}
```