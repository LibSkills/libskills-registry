# Pitfalls

```cpp
// PITFALL 1: Not checking parse errors
// BAD: No error checking
rapidjson::Document doc;
doc.Parse(invalid_json); // Crashes if invalid

// GOOD: Always check parse errors
rapidjson::Document doc;
doc.Parse(json_string);
if (doc.HasParseError()) {
    std::cerr << "Parse error at offset " << doc.GetErrorOffset() 
              << ": " << doc.GetParseError() << std::endl;
    return;
}

// PITFALL 2: Accessing non-existent members
// BAD: Direct access without checking
std::string name = doc["name"].GetString(); // Crashes if "name" doesn't exist

// GOOD: Check member existence
if (doc.HasMember("name") && doc["name"].IsString()) {
    std::string name = doc["name"].GetString();
}

// PITFALL 3: Type mismatch
// BAD: Assuming type
int age = doc["age"].GetInt(); // Crashes if "age" is a string

// GOOD: Check type before access
if (doc["age"].IsInt()) {
    int age = doc["age"].GetInt();
} else if (doc["age"].IsString()) {
    int age = std::stoi(doc["age"].GetString());
}

// PITFALL 4: Using dangling references after document modification
// BAD: Reference becomes invalid after modification
rapidjson::Document doc;
doc.Parse(R"({"items":[1,2,3]})");
auto& items = doc["items"]; // Reference to internal data
doc.AddMember("new", "value", doc.GetAllocator()); // May invalidate reference
items.GetArray(); // Undefined behavior!

// GOOD: Re-access after modification
doc.AddMember("new", "value", doc.GetAllocator());
auto& items = doc["items"]; // Fresh reference

// PITFALL 5: Memory management with in-situ parsing
// BAD: Input string goes out of scope
std::string get_json() {
    return R"({"data":"value"})";
}
void process() {
    std::string json = get_json();
    rapidjson::Document doc;
    doc.ParseInsitu(&json[0]); // Takes ownership of string buffer
    // doc now references json's internal buffer
} // json destroyed, doc has dangling pointer

// GOOD: Use non-insitu parsing or ensure string lifetime
std::string json = get_json();
rapidjson::Document doc;
doc.Parse(json.c_str()); // Makes copy of data

// PITFALL 6: Not handling null values
// BAD: Assuming value exists
if (doc["optional"].IsString()) { // Crashes if "optional" is null
    // ...
}

// GOOD: Check for null explicitly
if (doc["optional"].IsNull()) {
    // Handle null case
} else if (doc["optional"].IsString()) {
    // Process string
}

// PITFALL 7: Incorrect allocator usage
// BAD: Using temporary allocator
rapidjson::Document doc;
{
    rapidjson::Document::AllocatorType tempAlloc;
    doc.AddMember("key", "value", tempAlloc); // tempAlloc destroyed!
}

// GOOD: Use document's allocator
doc.AddMember("key", "value", doc.GetAllocator());

// PITFALL 8: Not handling deep copy correctly
// BAD: Shallow copy of values
rapidjson::Value v1;
v1.SetString("hello", doc.GetAllocator());
rapidjson::Value v2 = v1; // Shallow copy, v1 and v2 share memory

// GOOD: Deep copy
rapidjson::Value v2(v1, doc.GetAllocator()); // Deep copy
```