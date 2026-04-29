# nlohmann/json — Lifecycle

## Initialization

```cpp
#include <nlohmann/json.hpp>
using json = nlohmann::json;

// Empty (null)
json j;  // j.is_null() == true

// From literal
json j1 = "hello";          // string
json j2 = 42;               // number (integer)
json j3 = 3.14;             // number (float)
json j4 = true;             // boolean
json j5 = nullptr;          // null

// From initializer list (object)
json j = {
    {"name", "Alice"},
    {"age", 30},
    {"active", true},
    {"tags", {"admin", "user"}},
    {"address", {{"city", "NYC"}, {"zip", "10001"}}}
};

// From initializer list (array)
json arr = {1, 2, 3, 4, 5};

// Create empty object/array
json obj = json::object();  // {}
json arr = json::array();   // []
```

## Parsing

```cpp
// From string
std::string raw = R"({"name":"Alice","age":30})";
json j = json::parse(raw);

// From stream
std::ifstream file("data.json");
json j;
file >> j;

// With options
json j = json::parse(raw, nullptr, true, true); // allow_exceptions, allow_comments
```

## Modification

```cpp
json j = json::object();

// Add/update
j["name"] = "Bob";
j["scores"] = json::array({95, 87, 92});

// Emplace (returns iterator, bool)
auto [it, inserted] = j.emplace("key", "value");

// Erase
j.erase("name");           // by key
j["scores"].erase(1);      // by index
auto it = j.begin();
j.erase(it);               // by iterator

// Merge
json patch = {{"name", "Charlie"}};
j.merge_patch(patch);      // RFC 7396
```

## Serialization

```cpp
// Compact (default)
std::string s = j.dump();

// Pretty-print
std::string s = j.dump(2); // 2-space indent

// To stream
std::cout << j << std::endl;

// With format control
std::string s = j.dump(-1, ' ', false, json::error_handler_t::replace);
// indent=-1 (compact), indent_char=' ', ensure_ascii=false, error_handler=replace
```

## Destruction

`json` objects are automatically destroyed when they go out of scope. Internal reference counting handles shared small-string optimization.

```cpp
void fn() {
    json j = json::parse(large_file); // allocates
    // ... use j ...
} // j is destroyed, all memory freed
```

- No manual `free()` or `destroy()` needed
- Assignment / parameter passing uses shared ownership internally (copy-on-write for non-const access)
- Exception safety: if `parse()` throws, the partially-constructed object is cleaned up
- Move is O(1): `json j2 = std::move(j1); j1 = nullptr;`
