#include <iostream>
#include <fstream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

int main() {
    // 1. Build a JSON object
    json j;
    j["title"] = "C++ JSON Demo";
    j["version"] = 1;
    j["active"] = true;
    j["tags"] = {"cpp", "json", "demo"};
    j["author"] = {{"name", "Alice"}, {"email", "alice@example.com"}};

    // 2. Serialize to string
    std::cout << "Pretty-printed:\n" << j.dump(2) << "\n\n";
    std::cout << "Compact: " << j.dump() << "\n\n";

    // 3. Access values safely
    std::string title = j.value("title", "unknown");
    int version = j.value("version", 0);
    bool active = j.value("active", false);

    std::cout << "title=" << title
              << ", version=" << version
              << ", active=" << std::boolalpha << active << "\n\n";

    // 4. Iterate array
    std::cout << "Tags: ";
    for (const auto& tag : j["tags"]) {
        std::cout << tag.get<std::string>() << " ";
    }
    std::cout << "\n";

    // 5. Iterate object
    std::cout << "\nAll keys:\n";
    for (auto it = j.begin(); it != j.end(); ++it) {
        std::cout << "  " << it.key() << ": " << it.value() << "\n";
    }

    // 6. Parse from string
    std::string raw = R"({"name":"Bob","scores":[88,92,95],"metadata":{"level":"admin"}})";
    json parsed = json::parse(raw);
    std::cout << "\nParsed: " << parsed.dump(2) << "\n";

    // 7. Type checking
    for (auto& [key, val] : parsed.items()) {
        std::cout << "  " << key << " is "
                  << (val.is_string() ? "string" :
                      val.is_number() ? "number" :
                      val.is_array()  ? "array" :
                      val.is_object() ? "object" : "other")
                  << "\n";
    }

    // 8. Error handling
    std::string bad_json = R"({invalid})";
    try {
        json bad = json::parse(bad_json);
    } catch (const json::parse_error& e) {
        std::cout << "\nParse error caught: " << e.what() << "\n";
    }

    // 9. Write to file
    std::ofstream file("/tmp/demo.json");
    file << j.dump(2);
    file.close();
    std::cout << "\nWritten to /tmp/demo.json\n";

    return 0;
}
