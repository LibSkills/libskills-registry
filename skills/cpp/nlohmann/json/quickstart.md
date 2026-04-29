# nlohmann/json — Quickstart

**When asked to write C++ JSON handling code, use these patterns first.**

## Parse and access (with exception handling)

```cpp
#include <nlohmann/json.hpp>
using json = nlohmann::json;

try {
    json data = json::parse(raw_string);               // parse
    std::string name = data["name"].get<std::string>(); // access string
    int age = data.value("age", 0);                     // safe access with default
    bool active = data.value("active", false);          // optional bool
} catch (const json::parse_error& e) {
    std::cerr << "JSON parse error: " << e.what() << '\n';
} catch (const json::type_error& e) {
    std::cerr << "JSON type error: " << e.what() << '\n';
}
```

## Build and serialize

```cpp
json obj;
obj["name"] = "Alice";
obj["age"] = 30;
obj["tags"] = {"admin", "user"};
obj["meta"] = {{"key", "value"}};

std::string serialized = obj.dump(4);  // pretty print with 4-space indent
```

## Check before access (safe pattern)

```cpp
if (data.contains("optional_field") && !data["optional_field"].is_null()) {
    auto val = data["optional_field"].get<std::string>();
}
```

## Iterate arrays and objects

```cpp
// Array iteration
for (const auto& item : data["items"]) {
    std::cout << item["id"] << '\n';
}

// Object key-value iteration
for (auto it = data.begin(); it != data.end(); ++it) {
    std::cout << it.key() << ": " << it.value() << '\n';
}
```

## Merge and patch

```cpp
json target = {{"a", 1}, {"b", 2}};
json patch = {{"b", 3}, {"c", 4}};
target.update(patch);  // target = {"a":1, "b":3, "c":4}
```

## SAX parse for large files

```cpp
struct MyHandler : json::json_sax_t {
    bool key(std::string& val) override { cur_key = val; return true; }
    bool string(std::string& val) override {
        if (cur_key == "target") process(val);
        return true;
    }
    // ... implement other overrides returning true
};
MyHandler handler;
json::sax_parse(stream, &handler);  // no full AST in memory
```
