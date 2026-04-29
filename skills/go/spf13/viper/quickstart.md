# Quickstart

```cpp
// Quickstart: Common viper usage patterns

// Pattern 1: Basic configuration loading
#include <viper/viper.hpp>
#include <iostream>

int main() {
    viper::Viper v;
    v.set_config_name("config");
    v.set_config_type("yaml");
    v.add_config_path(".");
    
    if (auto err = v.read_in_config(); err) {
        std::cerr << "Error reading config: " << err.message() << "\n";
        return 1;
    }
    
    std::cout << "Server port: " << v.get_int("server.port") << "\n";
    return 0;
}

// Pattern 2: Setting default values
#include <viper/viper.hpp>

int main() {
    viper::Viper v;
    v.set_default("server.port", 8080);
    v.set_default("server.host", "localhost");
    v.set_default("database.url", "postgres://localhost:5432/mydb");
    
    // Now read config (defaults are overridden if config provides values)
    v.set_config_name("app");
    v.add_config_path(".");
    v.read_in_config();
    
    int port = v.get_int("server.port");
    std::string host = v.get_string("server.host");
    return 0;
}

// Pattern 3: Environment variable binding
#include <viper/viper.hpp>
#include <cstdlib>

int main() {
    viper::Viper v;
    v.set_config_name("config");
    v.add_config_path(".");
    
    // Bind environment variables
    v.bind_env("server.port", "SERVER_PORT");
    v.bind_env("server.host", "SERVER_HOST");
    v.bind_env("database.url", "DATABASE_URL");
    
    v.read_in_config();
    
    // Environment variables override config file values
    int port = v.get_int("server.port");
    return 0;
}

// Pattern 4: Reading from multiple config files
#include <viper/viper.hpp>

int main() {
    viper::Viper v;
    
    // Add multiple config paths
    v.add_config_path("/etc/myapp/");
    v.add_config_path("$HOME/.myapp");
    v.add_config_path(".");
    
    v.set_config_name("config");
    v.set_config_type("yaml");
    
    // First found config file is used
    v.read_in_config();
    
    // Merge additional configs
    v.merge_config_path("/opt/myapp/override.yaml");
    
    return 0;
}

// Pattern 5: Watching for config changes
#include <viper/viper.hpp>
#include <thread>
#include <chrono>

int main() {
    viper::Viper v;
    v.set_config_name("config");
    v.add_config_path(".");
    v.read_in_config();
    
    // Watch for changes (polling-based)
    v.on_config_change([](const viper::Viper& v) {
        std::cout << "Config changed! New port: " 
                  << v.get_int("server.port") << "\n";
    });
    
    // Start watching in background thread
    v.watch_config();
    
    std::this_thread::sleep_for(std::chrono::seconds(60));
    return 0;
}

// Pattern 6: Reading nested configuration
#include <viper/viper.hpp>

int main() {
    viper::Viper v;
    v.set_config_name("config");
    v.add_config_path(".");
    v.read_in_config();
    
    // Access nested values using dot notation
    std::string db_host = v.get_string("database.host");
    int db_port = v.get_int("database.port");
    
    // Get entire subsection as a map
    auto db_config = v.get_string_map("database");
    for (const auto& [key, value] : db_config) {
        std::cout << key << ": " << value << "\n";
    }
    
    return 0;
}

// Pattern 7: Type-safe access with defaults
#include <viper/viper.hpp>

int main() {
    viper::Viper v;
    v.set_config_name("config");
    v.add_config_path(".");
    v.read_in_config();
    
    // Safe access with fallback defaults
    int port = v.get_int("server.port", 8080);  // Default if not found
    std::string host = v.get_string("server.host", "localhost");
    bool debug = v.get_bool("debug", false);
    double timeout = v.get_double("timeout.seconds", 30.0);
    
    return 0;
}

// Pattern 8: Writing config changes
#include <viper/viper.hpp>

int main() {
    viper::Viper v;
    v.set_config_name("config");
    v.set_config_type("yaml");
    v.add_config_path(".");
    v.read_in_config();
    
    // Modify configuration
    v.set("server.port", 9090);
    v.set("debug", true);
    
    // Write changes back to file
    if (auto err = v.write_config(); err) {
        std::cerr << "Failed to write config: " << err.message() << "\n";
        return 1;
    }
    
    // Write to specific file
    if (auto err = v.write_config_as("new_config.yaml"); err) {
        std::cerr << "Failed to write config: " << err.message() << "\n";
        return 1;
    }
    
    return 0;
}
```