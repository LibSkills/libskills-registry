# nlohmann/json — Best Practices

## Use `ordered_json` When Key Order Matters

```cpp
#include <nlohmann/json.hpp>
using ordered_json = nlohmann::ordered_json;

ordered_json j;
j["z"] = 1;
j["a"] = 2;
std::cout << j.dump() << "\n"; // {"z":1,"a":2} — insertion order preserved
```

## Parse Once, Move the Result

```cpp
std::string raw = fetch_data();
json j = json::parse(std::move(raw)); // avoids copy of input string
```

## Use `value()` With Defaults For Optional Fields

```cpp
struct Config {
    std::string host = "localhost";
    int port = 8080;
    bool debug = false;
};

Config parse_config(const json& j) {
    return Config{
        .host  = j.value("host", "localhost"),
        .port  = j.value("port", 8080),
        .debug = j.value("debug", false),
    };
}
```

## Specialize `adl_serializer` For Custom Types

```cpp
namespace nlohmann {
template <>
struct adl_serializer<MyPoint> {
    static void to_json(json& j, const MyPoint& p) {
        j = json{{"x", p.x}, {"y", p.y}};
    }
    static void from_json(const json& j, MyPoint& p) {
        j.at("x").get_to(p.x);
        j.at("y").get_to(p.y);
    }
};
}

// Usage: automatic conversion
MyPoint p{1, 2};
json j = p;                    // to_json
MyPoint p2 = j.get<MyPoint>(); // from_json
```

## Prefer SAX For Large Files

SAX parsing avoids building the tree. Use when you only need specific values or want to process incrementally.

```cpp
struct MyHandler : json::sax_t {
    bool null() override { return true; }
    bool boolean(bool v) override { return true; }
    bool number_integer(number_integer_t v) override {
        // process number
        return true;
    }
    bool key(string_t& v) override { return true; }
    bool start_object(std::size_t elements) override { return true; }
    bool end_object() override { return true; }
    bool start_array(std::size_t elements) override { return true; }
    bool end_array() override { return true; }
    bool string(string_t& v) override { return true; }
    bool binary(binary_t& v) override { return true; }
    bool parse_error(std::size_t position, const std::string& token, const json::exception& e) override {
        return false;
    }
};

// Use SAX parser (<10% memory of tree parse)
std::ifstream file("data.json");
MyHandler handler;
json::sax_parse(file, &handler);
```

## Use Binary Format (BSON/CBOR/MessagePack) For Internal Use

```cpp
// Convert JSON to CBOR (compact binary, ~30% of JSON size)
std::vector<std::uint8_t> cbor = json::to_cbor(j);

// Convert back
json j2 = json::from_cbor(cbor);

// Also available: to_bson, from_bson, to_msgpack, from_msgpack, to_ubjson
```
