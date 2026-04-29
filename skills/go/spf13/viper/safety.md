# Safety

```cpp
// Safety: Conditions that must NEVER occur

// Condition 1: NEVER use viper without setting config paths
#include <viper/viper.hpp>

// BAD: No config paths set
void unsafe_example1() {
    viper::Viper v;
    v.set_config_name("config");
    // Missing: v.add_config_path(".");
    v.read_in_config();  // Will always fail to find file
}

// GOOD: Always set at least one config path
void safe_example1() {
    viper::Viper v;
    v.set_config_name("config");
    v.add_config_path(".");  // Search current directory
    v.add_config_path("/etc/myapp/");  // Also search system config
    v.read_in_config();
}

// Condition 2: NEVER access config before reading
#include <viper/viper.hpp>

// BAD: Accessing config before read
void unsafe_example2() {
    viper::Viper v;
    v.set_config_name("config");
    v.add_config_path(".");
    // Forgot to call read_in_config()
    int port = v.get_int("port");  // Returns 0, not config value
}

// GOOD: Always read config before access
void safe_example2() {
    viper::Viper v;
    v.set_config_name("config");
    v.add_config_path(".");
    v.read_in_config();
    int port = v.get_int("port", 8080);  // Safe with default
}

// Condition 3: NEVER use uninitialized viper instance
#include <viper/viper.hpp>

// BAD: Using default-constructed viper without setup
void unsafe_example3() {
    viper::Viper v;  // Default constructed
    v.read_in_config();  // No config name set - will fail
}

// GOOD: Always configure before use
void safe_example3() {
    viper::Viper v;
    v.set_config_name("app");
    v.set_config_type("yaml");
    v.add_config_path(".");
    v.read_in_config();
}

// Condition 4: NEVER ignore type mismatches
#include <viper/viper.hpp>

// BAD: Assuming type without checking
void unsafe_example4() {
    viper::Viper v;
    v.set("port", "8080");  // String, not int
    int port = v.get_int("port");  // Returns 0, no error!
}

// GOOD: Use consistent types
void safe_example4() {
    viper::Viper v;
    v.set("port", 8080);  // Integer
    int port = v.get_int("port");  // Works correctly
    
    // Or use string consistently
    v.set("port_str", "8080");
    std::string port_str = v.get_string("port_str");
}

// Condition 5: NEVER modify config while iterating
#include <viper/viper.hpp>

// BAD: Modifying during iteration
void unsafe_example5() {
    viper::Viper v;
    v.read_in_config();
    
    auto keys = v.all_keys();
    for (const auto& key : keys) {
        if (key.find("temp_") == 0) {
            v.set(key, "modified");  // Modifying during iteration
        }
    }
}

// GOOD: Collect modifications first, then apply
void safe_example5() {
    viper::Viper v;
    v.read_in_config();
    
    std::vector<std::string> to_modify;
    auto keys = v.all_keys();
    for (const auto& key : keys) {
        if (key.find("temp_") == 0) {
            to_modify.push_back(key);
        }
    }
    
    for (const auto& key : to_modify) {
        v.set(key, "modified");  // Safe after iteration
    }
}
```