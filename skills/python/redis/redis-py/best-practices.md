# Best Practices

**Connection Pooling for Production**
```cpp
#include <sw/redis++/redis++.h>
#include <memory>

class RedisPool {
    std::unique_ptr<sw::redis::Redis> redis;
public:
    RedisPool() {
        ConnectionPoolOptions pool_opts;
        pool_opts.size = 10;  // Pool size
        pool_opts.wait_timeout = std::chrono::milliseconds(100);
        
        ConnectionOptions conn_opts;
        conn_opts.host = "127.0.0.1";
        conn_opts.port = 6379;
        conn_opts.connect_timeout = std::chrono::milliseconds(100);
        
        redis = std::make_unique<sw::redis::Redis>(conn_opts, pool_opts);
    }
    
    void set_with_retry(const std::string &key, const std::string &val, int retries = 3) {
        for (int i = 0; i < retries; ++i) {
            try {
                redis->set(key, val);
                return;
            } catch (const sw::redis::Error &e) {
                if (i == retries - 1) throw;
                std::this_thread::sleep_for(std::chrono::milliseconds(100 * (i + 1)));
            }
        }
    }
};
```

**Using Pipelines for Batch Operations**
```cpp
void batch_insert(const std::vector<std::pair<std::string, std::string>> &items) {
    auto redis = Redis("tcp://127.0.0.1:6379");
    
    const size_t BATCH_SIZE = 100;
    for (size_t i = 0; i < items.size(); i += BATCH_SIZE) {
        auto pipe = redis.pipeline();
        for (size_t j = i; j < std::min(i + BATCH_SIZE, items.size()); ++j) {
            pipe.set(items[j].first, items[j].second);
        }
        pipe.exec();  // Execute batch
    }
}
```

**Proper Error Handling with Custom Exceptions**
```cpp
class RedisException : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

class RedisClient {
    sw::redis::Redis redis;
public:
    RedisClient() : redis("tcp://127.0.0.1:6379") {}
    
    std::string get_or_throw(const std::string &key) {
        try {
            auto val = redis.get(key);
            if (!val) {
                throw RedisException("Key not found: " + key);
            }
            return *val;
        } catch (const sw::redis::Error &e) {
            throw RedisException(std::string("Redis error: ") + e.what());
        }
    }
};
```

**Using Lua Scripts for Atomic Operations**
```cpp
void atomic_transfer(const std::string &from, const std::string &to, int amount) {
    auto redis = Redis("tcp://127.0.0.1:6379");
    
    std::string script = R"(
        local from_bal = redis.call('GET', KEYS[1])
        local to_bal = redis.call('GET', KEYS[2])
        if not from_bal or tonumber(from_bal) < tonumber(ARGV[1]) then
            return false
        end
        redis.call('SET', KEYS[1], tonumber(from_bal) - tonumber(ARGV[1]))
        redis.call('SET', KEYS[2], tonumber(to_bal) + tonumber(ARGV[1]))
        return true
    )";
    
    auto result = redis.eval<long long>(script, {from, to}, {std::to_string(amount)});
    if (!result) {
        throw std::runtime_error("Transfer failed: insufficient funds");
    }
}
```