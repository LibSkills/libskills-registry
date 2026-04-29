# Best Practices

```cpp
// Best Practices: Production-ready viper usage

// Practice 1: Centralized configuration class
#include <viper/viper.hpp>
#include <memory>
#include <mutex>

class AppConfig {
private:
    viper::Viper v_;
    std::mutex mtx_;
    
public:
    AppConfig() {
        v_.set_config_name("app");
        v_.set_config_type("yaml");
        v_.add_config_path(".");
        v_.add_config_path("/etc/myapp/");
        v_.add_config_path("$HOME/.myapp");
        
        // Set defaults
        v_.set_default("server.port", 8080);
        v_.set_default("server.host", "0.0.0.0");
        v_.set_default("log.level", "info");
        v_.set_default("database.max_connections", 10);
        
        // Bind environment variables
        v_.set_env_prefix("MYAPP");
        v_.bind_env("server.port", "MYAPP_PORT");
        v_.bind_env("log.level", "MYAPP_LOG_LEVEL");
        
        reload();
    }
    
    void reload() {
        std::lock_guard<std::mutex> lock(mtx_);
        if (auto err = v_.read_in_config(); err) {
            // Log warning but continue with defaults
            std::cerr << "Config warning: " << err.message() << "\n";
        }
    }
    
    int get_port() const {
        std::lock_guard<std::mutex> lock(mtx_);
        return v_.get_int("server.port");
    }
    
    std::string get_host() const {
        std::lock_guard<std::mutex> lock(mtx_);
        return v_.get_string("server.host");
    }
};

// Practice 2: Configuration validation
#include <viper/viper.hpp>
#include <optional>

class ValidatedConfig {
private:
    viper::Viper v_;
    
    struct ValidationResult {
        bool valid;
        std::vector<std::string> errors;
    };
    
    ValidationResult validate() {
        ValidationResult result{true, {}};
        
        // Check required keys
        std::vector<std::pair<std::string, std::string>> required = {
            {"server.port", "integer"},
            {"database.url", "string"},
            {"log.level", "string"}
        };
        
        for (const auto& [key, type] : required) {
            if (!v_.is_set(key)) {
                result.valid = false;
                result.errors.push_back("Missing required: " + key);
            }
        }
        
        // Validate port range
        if (v_.is_set("server.port")) {
            int port = v_.get_int("server.port");
            if (port < 1 || port > 65535) {
                result.valid = false;
                result.errors.push_back("Port out of range: " + std::to_string(port));
            }
        }
        
        return result;
    }
    
public:
    bool load() {
        v_.set_config_name("app");
        v_.set_config_type("yaml");
        v_.add_config_path(".");
        
        if (auto err = v_.read_in_config(); err) {
            std::cerr << "Config error: " << err.message() << "\n";
            return false;
        }
        
        auto validation = validate();
        if (!validation.valid) {
            for (const auto& error : validation.errors) {
                std::cerr << "Validation error: " << error << "\n";
            }
            return false;
        }
        
        return true;
    }
};

// Practice 3: Environment-specific configuration
#include <viper/viper.hpp>

class EnvironmentConfig {
private:
    viper::Viper v_;
    std::string environment_;
    
public:
    EnvironmentConfig() {
        // Determine environment
        const char* env = std::getenv("APP_ENV");
        environment_ = env ? env : "development";
        
        v_.set_config_type("yaml");
        
        // Load base config
        v_.set_config_name("config");
        v_.add_config_path(".");
        v_.read_in_config();
        
        // Load environment-specific overrides
        std::string env_config = "config." + environment_;
        v_.set_config_name(env_config);
        v_.read_in_config();  // Merge overrides
    }
    
    std::string get_database_url() const {
        return v_.get_string("database.url", "postgres://localhost:5432/mydb");
    }
};

// Practice 4: Config change notification
#include <viper/viper.hpp>
#include <functional>
#include <vector>

class ObservableConfig {
private:
    viper::Viper v_;
    std::vector<std::function<void()>> observers_;
    
public:
    ObservableConfig() {
        v_.set_config_name("app");
        v_.add_config_path(".");
        v_.read_in_config();
        
        // Watch for changes
        v_.on_config_change([this](const viper::Viper&) {
            notify_observers();
        });
    }
    
    void add_observer(std::function<void()> observer) {
        observers_.push_back(std::move(observer));
    }
    
    void notify_observers() {
        for (const auto& observer : observers_) {
            observer();
        }
    }
};

// Practice 5: Config caching for performance
#include <viper/viper.hpp>
#include <unordered_map>

class CachedConfig {
private:
    viper::Viper v_;
    mutable std::unordered_map<std::string, std::string> cache_;
    mutable std::mutex cache_mtx_;
    
public:
    CachedConfig() {
        v_.set_config_name("app");
        v_.add_config_path(".");
        v_.read_in_config();
    }
    
    std::string get(const std::string& key) const {
        std::lock_guard<std::mutex> lock(cache_mtx_);
        
        auto it = cache_.find(key);
        if (it != cache_.end()) {
            return it->second;
        }
        
        std::string value = v_.get_string(key, "");
        cache_[key] = value;
        return value;
    }
    
    void invalidate_cache() {
        std::lock_guard<std::mutex> lock(cache_mtx_);
        cache_.clear();
    }
};
```