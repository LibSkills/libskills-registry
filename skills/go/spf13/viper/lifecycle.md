# Lifecycle

```cpp
// Lifecycle: Construction, destruction, and resource management

// Construction patterns
#include <viper/viper.hpp>
#include <memory>

// Pattern 1: Default construction with setup
class ConfigManager {
private:
    viper::Viper v_;
    
public:
    ConfigManager() {
        // Construction sets up defaults
        v_.set_config_name("app");
        v_.set_config_type("yaml");
        v_.add_config_path(".");
        v_.set_default("port", 8080);
        v_.set_default("host", "localhost");
    }
    
    // Move constructor
    ConfigManager(ConfigManager&& other) noexcept 
        : v_(std::move(other.v_)) {}
    
    // Move assignment
    ConfigManager& operator=(ConfigManager&& other) noexcept {
        if (this != &other) {
            v_ = std::move(other.v_);
        }
        return *this;
    }
    
    // Destructor - viper handles cleanup automatically
    ~ConfigManager() = default;
    
    void load() {
        if (auto err = v_.read_in_config(); err) {
            throw std::runtime_error(err.message());
        }
    }
};

// Pattern 2: Factory function for construction
std::unique_ptr<viper::Viper> create_config(const std::string& app_name) {
    auto v = std::make_unique<viper::Viper>();
    v->set_config_name(app_name);
    v->set_config_type("yaml");
    v->add_config_path(".");
    v->add_config_path("/etc/" + app_name + "/");
    v->add_config_path("$HOME/." + app_name + "/");
    
    v->set_default("port", 8080);
    v->set_default("log_level", "info");
    
    return v;
}

// Pattern 3: Resource management with RAII
#include <viper/viper.hpp>
#include <fstream>

class ConfigResource {
private:
    viper::Viper v_;
    std::string config_path_;
    
public:
    ConfigResource(const std::string& path) 
        : config_path_(path) {
        v_.set_config_name("app");
        v_.set_config_type("yaml");
        v_.add_config_path(path);
    }
    
    // Copy is disabled (viper doesn't support copy)
    ConfigResource(const ConfigResource&) = delete;
    ConfigResource& operator=(const ConfigResource&) = delete;
    
    // Move is supported
    ConfigResource(ConfigResource&& other) noexcept 
        : v_(std::move(other.v_)), 
          config_path_(std::move(other.config_path_)) {}
    
    ~ConfigResource() {
        // Cleanup if needed
        if (!config_path_.empty()) {
            // viper handles its own cleanup
        }
    }
    
    void reload() {
        v_.read_in_config();
    }
};

// Pattern 4: Lifetime management with shared_ptr
#include <memory>

class SharedConfig {
private:
    std::shared_ptr<viper::Viper> v_;
    
public:
    SharedConfig() 
        : v_(std::make_shared<viper::Viper>()) {
        v_->set_config_name("shared");
        v_->set_config_type("yaml");
        v_->add_config_path(".");
    }
    
    std::shared_ptr<viper::Viper> get() const {
        return v_;
    }
};

// Pattern 5: Proper cleanup sequence
#include <viper/viper.hpp>

class ManagedConfig {
private:
    viper::Viper v_;
    bool loaded_ = false;
    
public:
    void initialize() {
        v_.set_config_name("app");
        v_.add_config_path(".");
        v_.read_in_config();
        loaded_ = true;
    }
    
    void shutdown() {
        if (loaded_) {
            // Perform any cleanup before destruction
            // viper doesn't have explicit cleanup, but
            // we can save state if needed
            v_.write_config();  // Save current state
            loaded_ = false;
        }
    }
    
    ~ManagedConfig() {
        shutdown();  // Ensure cleanup
    }
};

// Pattern 6: Singleton with proper lifecycle
class ConfigSingleton {
private:
    static std::unique_ptr<viper::Viper> instance_;
    static std::once_flag init_flag_;
    
public:
    static viper::Viper& get() {
        std::call_once(init_flag_, []() {
            instance_ = std::make_unique<viper::Viper>();
            instance_->set_config_name("app");
            instance_->set_config_type("yaml");
            instance_->add_config_path(".");
            instance_->read_in_config();
        });
        return *instance_;
    }
    
    static void reset() {
        instance_.reset();
        init_flag_ = std::once_flag();
    }
};

std::unique_ptr<viper::Viper> ConfigSingleton::instance_;
std::once_flag ConfigSingleton::init_flag_;
```