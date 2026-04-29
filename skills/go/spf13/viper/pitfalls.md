# Pitfalls

```cpp
// Pitfalls: Common mistakes with viper

// Pitfall 1: Not checking read_in_config() return value
#include <viper/viper.hpp>

// BAD: Ignoring error
void bad_example() {
    viper::Viper v;
    v.set_config_name("config");
    v.add_config_path(".");
    v.read_in_config();  // Error ignored!
    int port = v.get_int("port");  // May return 0 or crash
}

// GOOD: Proper error handling
void good_example() {
    viper::Viper v;
    v.set_config_name("config");
    v.add_config_path(".");
    
    if (auto err = v.read_in_config(); err) {
        std::cerr << "Config error: " << err.message() << "\n";
        return;
    }
    int port = v.get_int("port", 8080);  // Safe with default
}

// Pitfall 2: Forgetting to set config type
#include <viper/viper.hpp>

// BAD: No config type specified
void bad_example2() {
    viper::Viper v;
    v.set_config_name("config");  // No extension, no type
    v.add_config_path(".");
    v.read_in_config();  // May fail to find file
}

// GOOD: Specify config type or use extension
void good_example2() {
    viper::Viper v;
    v.set_config_name("config");
    v.set_config_type("yaml");  // Explicit type
    v.add_config_path(".");
    v.read_in_config();
}

// Pitfall 3: Case sensitivity issues
#include <viper/viper.hpp>

// BAD: Assuming case-insensitive keys
void bad_example3() {
    viper::Viper v;
    v.set("ServerPort", 8080);
    int port = v.get_int("serverport");  // Returns 0, not 8080!
}

// GOOD: Consistent key naming
void good_example3() {
    viper::Viper v;
    v.set("server.port", 8080);
    int port = v.get_int("server.port");  // Works correctly
}

// Pitfall 4: Not handling missing keys
#include <viper/viper.hpp>

// BAD: No default value
void bad_example4() {
    viper::Viper v;
    v.read_in_config();
    int port = v.get_int("nonexistent.key");  // Returns 0 silently
}

// GOOD: Provide sensible defaults
void good_example4() {
    viper::Viper v;
    v.read_in_config();
    int port = v.get_int("nonexistent.key", 8080);  // Returns 8080
}

// Pitfall 5: Environment variable binding confusion
#include <viper/viper.hpp>

// BAD: Wrong environment variable name
void bad_example5() {
    viper::Viper v;
    v.bind_env("port", "PORT");  // May conflict with system PORT
    v.read_in_config();
}

// GOOD: Use application-specific prefix
void good_example5() {
    viper::Viper v;
    v.set_env_prefix("MYAPP");
    v.bind_env("port", "MYAPP_PORT");  // Clear and specific
    v.read_in_config();
}

// Pitfall 6: Modifying config while reading
#include <viper/viper.hpp>
#include <thread>

// BAD: Concurrent modification
void bad_example6() {
    viper::Viper v;
    v.read_in_config();
    
    std::thread t1([&]() { v.set("key1", "value1"); });
    std::thread t2([&]() { v.get_string("key2"); });
    
    t1.join();
    t2.join();  // Undefined behavior!
}

// GOOD: Use mutex for concurrent access
void good_example6() {
    viper::Viper v;
    std::mutex mtx;
    v.read_in_config();
    
    std::thread t1([&]() { 
        std::lock_guard<std::mutex> lock(mtx);
        v.set("key1", "value1"); 
    });
    std::thread t2([&]() { 
        std::lock_guard<std::mutex> lock(mtx);
        v.get_string("key2"); 
    });
    
    t1.join();
    t2.join();
}

// Pitfall 7: Not handling config file format errors
#include <viper/viper.hpp>

// BAD: Assuming valid config
void bad_example7() {
    viper::Viper v;
    v.set_config_name("config");
    v.set_config_type("yaml");
    v.add_config_path(".");
    v.read_in_config();  // If YAML is malformed, this silently fails
}

// GOOD: Validate config after reading
void good_example7() {
    viper::Viper v;
    v.set_config_name("config");
    v.set_config_type("yaml");
    v.add_config_path(".");
    
    auto err = v.read_in_config();
    if (err) {
        std::cerr << "Config parse error: " << err.message() << "\n";
        return;
    }
    
    // Validate required keys exist
    if (!v.is_set("server.port")) {
        std::cerr << "Missing required key: server.port\n";
        return;
    }
}
```