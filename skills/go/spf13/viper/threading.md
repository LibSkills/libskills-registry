# Threading

```cpp
// Threading: Thread safety and concurrent access

// Thread safety guarantees
#include <viper/viper.hpp>
#include <thread>
#include <mutex>
#include <vector>

/*
 * viper's thread safety:
 * - NOT thread-safe by default
 * - Concurrent reads are safe (const methods)
 * - Concurrent writes are NOT safe
 * - Read-modify-write patterns need synchronization
 * - Config watching runs in its own thread
 */

// Pattern 1: Thread-safe wrapper with mutex
#include <mutex>

class ThreadSafeConfig {
private:
    viper::Viper v_;
    mutable std::shared_mutex mtx_;  // C++17 shared_mutex
    
public:
    void load() {
        std::lock_guard<std::shared_mutex> lock(mtx_);
        v_.set_config_name("app");
        v_.set_config_type("yaml");
        v_.add_config_path(".");
        v_.read_in_config();
    }
    
    int get_port() const {
        std::shared_lock<std::shared_mutex> lock(mtx_);  // Shared lock for reads
        return v_.get_int("server.port", 8080);
    }
    
    void set_port(int port) {
        std::lock_guard<std::shared_mutex> lock(mtx_);  // Exclusive lock for writes
        v_.set("server.port", port);
    }
    
    void reload() {
        std::lock_guard<std::shared_mutex> lock(mtx_);
        v_.read_in_config();
    }
};

// Pattern 2: Read-write lock for concurrent access
#include <shared_mutex>

class ReadWriteConfig {
private:
    viper::Viper v_;
    mutable std::shared_mutex rw_mutex_;
    
public:
    // Multiple threads can read simultaneously
    std::string get(const std::string& key) const {
        std::shared_lock<std::shared_mutex> lock(rw_mutex_);
        return v_.get_string(key, "");
    }
    
    // Only one thread can write at a time
    void set(const std::string& key, const std::string& value) {
        std::lock_guard<std::shared_mutex> lock(rw_mutex_);
        v_.set(key, value);
    }
};

// Pattern 3: Thread-safe config with atomic operations
#include <atomic>

class AtomicConfig {
private:
    viper::Viper v_;
    std::mutex mtx_;
    std::atomic<int> port_{8080};  // Cache for fast reads
    std::atomic<bool> dirty_{false};
    
public:
    void load() {
        std::lock_guard<std::mutex> lock(mtx_);
        v_.read_in_config();
        port_.store(v_.get_int("server.port", 8080));
        dirty_.store(false);
    }
    
    int get_port() const {
        if (dirty_.load()) {
            // Need to reload
            const_cast<AtomicConfig*>(this)->load();
        }
        return port_.load();  // Fast atomic read
    }
    
    void set_port(int port) {
        std::lock_guard<std::mutex> lock(mtx_);
        v_.set("server.port", port);
        port_.store(port);
        dirty_.store(true);
    }
};

// Pattern 4: Thread-safe config watching
#include <functional>

class WatchableConfig {
private:
    viper::Viper v_;
    std::mutex mtx_;
    std::thread watcher_;
    std::atomic<bool> running_{false};
    std::function<void()> callback_;
    
public:
    void start_watching(std::function<void()> callback) {
        callback_ = std::move(callback);
        running_.store(true);
        
        watcher_ = std::thread([this]() {
            while (running_.load()) {
                std::this_thread::sleep_for(std::chrono::seconds(5));
                
                std::lock_guard<std::mutex> lock(mtx_);
                if (auto err = v_.read_in_config(); !err) {
                    if (callback_) {
                        callback_();
                    }
                }
            }
        });
    }
    
    void stop_watching() {
        running_.store(false);
        if (watcher_.joinable()) {
            watcher_.join();
        }
    }
    
    ~WatchableConfig() {
        stop_watching();
    }
};

// Pattern 5: Thread-safe config with copy-on-write
#include <memory>

class CopyOnWriteConfig {
private:
    std::shared_ptr<viper::Viper> current_;
    std::mutex write_mutex_;
    
public:
    CopyOnWriteConfig() 
        : current_(std::make_shared<viper::Viper>()) {
        current_->set_config_name("app");
        current_->set_config_type("yaml");
        current_->add_config_path(".");
        current_->read_in_config();
    }
    
    // Thread-safe read
    std::shared_ptr<const viper::Viper> read() const {
        return std::atomic_load(&current_);
    }
    
    // Thread-safe write (creates new instance)
    void write(const std::string& key, const std::string& value) {
        std::lock_guard<std::mutex> lock(write_mutex_);
        
        auto new_config = std::make_shared<viper::Viper>(*current_);
        new_config->set(key, value);
        
        std::atomic_store(&current_, new_config);
    }
};

// Pattern 6: Thread-safe config pool
#include <vector>

class ConfigPool {
private:
    std::vector<std::unique_ptr<viper::Viper>> pool_;
    std::mutex pool_mutex_;
    std::atomic<size_t> index_{0};
    
public:
    ConfigPool(size_t size) {
        for (size_t i = 0; i < size; ++i) {
            auto v = std::make_unique<viper::Viper>();
            v->set_config_name("app");
            v->set_config_type("yaml");
            v->add_config_path(".");
            v->read_in_config();
            pool_.push_back(std::move(v));
        }
    }
    
    viper::Viper& get() {
        // Round-robin access, no locking needed for reads
        size_t idx = index_.fetch_add(1) % pool_.size();
        return *pool_[idx];
    }
    
    void reload_all() {
        std::lock_guard<std::mutex> lock(pool_mutex_);
        for (auto& v : pool_) {
            v->read_in_config();
        }
    }
};
```