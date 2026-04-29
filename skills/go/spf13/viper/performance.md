# Performance

```cpp
// Performance: Characteristics and optimization

// Performance characteristics
#include <viper/viper.hpp>
#include <chrono>
#include <iostream>

/*
 * Key performance facts:
 * - Config reading is O(n) where n is config size
 * - Key lookup is O(log n) using internal tree structure
 * - Type conversion adds overhead (string to int, etc.)
 * - Environment variable binding adds startup cost
 * - Config watching uses polling (configurable interval)
 */

// Benchmark: Key lookup performance
void benchmark_lookup() {
    viper::Viper v;
    v.set_config_name("large_config");
    v.set_config_type("yaml");
    v.add_config_path(".");
    v.read_in_config();
    
    auto start = std::chrono::high_resolution_clock::now();
    
    // Perform 10000 lookups
    for (int i = 0; i < 10000; ++i) {
        int port = v.get_int("server.port");
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    std::cout << "10000 lookups took: " << duration.count() << " microseconds\n";
}

// Optimization 1: Cache frequently accessed values
#include <unordered_map>

class OptimizedConfig {
private:
    viper::Viper v_;
    mutable std::unordered_map<std::string, int> int_cache_;
    mutable std::unordered_map<std::string, std::string> string_cache_;
    mutable std::mutex cache_mutex_;
    
public:
    int get_int_cached(const std::string& key) const {
        std::lock_guard<std::mutex> lock(cache_mutex_);
        
        auto it = int_cache_.find(key);
        if (it != int_cache_.end()) {
            return it->second;
        }
        
        int value = v_.get_int(key, 0);
        int_cache_[key] = value;
        return value;
    }
    
    void invalidate_cache() {
        std::lock_guard<std::mutex> lock(cache_mutex_);
        int_cache_.clear();
        string_cache_.clear();
    }
};

// Optimization 2: Batch reads for multiple values
#include <vector>

class BatchConfigReader {
private:
    viper::Viper v_;
    
public:
    struct ServerConfig {
        int port;
        std::string host;
        bool tls_enabled;
        int max_connections;
    };
    
    ServerConfig read_server_config() {
        // Batch read reduces lookup overhead
        ServerConfig config;
        config.port = v_.get_int("server.port", 8080);
        config.host = v_.get_string("server.host", "localhost");
        config.tls_enabled = v_.get_bool("server.tls", false);
        config.max_connections = v_.get_int("server.max_connections", 100);
        return config;
    }
};

// Optimization 3: Avoid repeated type conversions
#include <string>

class TypeSafeConfig {
private:
    viper::Viper v_;
    int port_;
    std::string host_;
    bool initialized_ = false;
    
public:
    void initialize() {
        // Do all type conversions once
        port_ = v_.get_int("server.port", 8080);
        host_ = v_.get_string("server.host", "localhost");
        initialized_ = true;
    }
    
    int get_port() const {
        return port_;  // No type conversion overhead
    }
    
    std::string get_host() const {
        return host_;  // No type conversion overhead
    }
};

// Optimization 4: Use appropriate config format
#include <viper/viper.hpp>

/*
 * Performance by format (approximate):
 * JSON: Fastest parsing, moderate memory
 * YAML: Slower parsing, more memory
 * TOML: Moderate parsing, compact
 * HCL: Slowest parsing, most memory
 * 
 * For performance-critical apps, prefer JSON
 */

void choose_format() {
    viper::Viper v;
    
    // JSON is fastest for parsing
    v.set_config_type("json");
    v.set_config_name("config");
    v.add_config_path(".");
    
    auto start = std::chrono::high_resolution_clock::now();
    v.read_in_config();
    auto end = std::chrono::high_resolution_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    std::cout << "JSON parse time: " << duration.count() << " microseconds\n";
}

// Optimization 5: Minimize config file size
#include <viper/viper.hpp>

/*
 * Tips for smaller configs:
 * - Remove comments in production
 * - Use shorter key names
 * - Flatten nested structures
 * - Remove unused keys
 * - Use environment variables for dynamic values
 */

void optimize_config_size() {
    // Instead of deeply nested:
    // server:
    //   database:
    //     connection:
    //       host: localhost
    //       port: 5432
    
    // Use flat keys:
    // db_host: localhost
    // db_port: 5432
    
    viper::Viper v;
    v.set_config_type("yaml");
    v.set_config_name("optimized_config");
    v.add_config_path(".");
    v.read_in_config();
    
    // Flat key access is faster
    std::string host = v.get_string("db_host", "localhost");
    int port = v.get_int("db_port", 5432);
}
```