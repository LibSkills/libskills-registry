# Threading

### Thread Safety Guarantees
```cpp
// tsl::robin_map provides the same thread safety guarantees as std::unordered_map
// Multiple concurrent readers are safe
// Concurrent writers or mixed reader/writer access requires synchronization

// SAFE: Multiple readers
tsl::robin_map<int, int> map = {{1, 10}, {2, 20}};
std::vector<std::thread> readers;
for (int i = 0; i < 4; ++i) {
    readers.emplace_back([&map]() {
        for (int j = 0; j < 100; ++j) {
            auto it = map.find(1);  // Safe: concurrent reads
            if (it != map.end()) {
                volatile int val = it->second;
            }
        }
    });
}
for (auto& t : readers) t.join();
```

### Concurrent Write Protection
```cpp
// UNSAFE: Concurrent writes without synchronization
tsl::robin_map<int, int> map;
std::vector<std::thread> writers;
for (int i = 0; i < 10; ++i) {
    writers.emplace_back([&map, i]() {
        map[i] = i;  // Data race!
    });
}

// SAFE: Use mutex for write protection
tsl::robin_map<int, int> safe_map;
std::mutex mtx;
std::vector<std::thread> safe_writers;
for (int i = 0; i < 10; ++i) {
    safe_writers.emplace_back([&safe_map, &mtx, i]() {
        std::lock_guard<std::mutex> lock(mtx);
        safe_map[i] = i;  // Protected by mutex
    });
}
for (auto& t : safe_writers) t.join();
```

### Read-Write Lock Pattern
```cpp
// Use shared_mutex for better read concurrency
#include <shared_mutex>

class ThreadSafeRobinMap {
    tsl::robin_map<int, int> map_;
    mutable std::shared_mutex mtx_;
    
public:
    void insert(int key, int value) {
        std::unique_lock<std::shared_mutex> lock(mtx_);
        map_[key] = value;
    }
    
    std::optional<int> find(int key) const {
        std::shared_lock<std::shared_mutex> lock(mtx_);
        auto it = map_.find(key);
        if (it != map_.end()) {
            return it->second;
        }
        return std::nullopt;
    }
    
    void clear() {
        std::unique_lock<std::shared_mutex> lock(mtx_);
        map_.clear();
    }
};

// Usage
ThreadSafeRobinMap thread_safe_map;
std::vector<std::thread> threads;

// Multiple concurrent readers
for (int i = 0; i < 4; ++i) {
    threads.emplace_back([&thread_safe_map]() {
        for (int j = 0; j < 100; ++j) {
            auto val = thread_safe_map.find(1);
        }
    });
}

// Occasional writers
threads.emplace_back([&thread_safe_map]() {
    thread_safe_map.insert(1, 100);
});

for (auto& t : threads) t.join();
```

### Fine-Grained Locking Strategy
```cpp
// For high-contention scenarios, consider sharding
template<typename Key, typename Value, int NumShards = 16>
class ShardedRobinMap {
    std::vector<tsl::robin_map<Key, Value>> shards_;
    std::vector<std::mutex> mutexes_;
    
    std::size_t get_shard_index(const Key& key) const {
        return std::hash<Key>{}(key) % NumShards;
    }
    
public:
    ShardedRobinMap() : shards_(NumShards), mutexes_(NumShards) {}
    
    void insert(const Key& key, const Value& value) {
        auto idx = get_shard_index(key);
        std::lock_guard<std::mutex> lock(mutexes_[idx]);
        shards_[idx][key] = value;
    }
    
    std::optional<Value> find(const Key& key) const {
        auto idx = get_shard_index(key);
        std::lock_guard<std::mutex> lock(mutexes_[idx]);
        auto it = shards_[idx].find(key);
        if (it != shards_[idx].end()) {
            return it->second;
        }
        return std::nullopt;
    }
};

// Usage with high concurrency
ShardedRobinMap<int, int> sharded_map;
std::vector<std::thread> workers;
for (int i = 0; i < 16; ++i) {
    workers.emplace_back([&sharded_map, i]() {
        for (int j = 0; j < 1000; ++j) {
            sharded_map.insert(i * 1000 + j, j);
            auto val = sharded_map.find(i * 1000 + j);
        }
    });
}
for (auto& t : workers) t.join();
```

### Thread-Local Storage Pattern
```cpp
// For write-heavy workloads, use thread-local maps and merge
class ThreadLocalAggregator {
    std::vector<tsl::robin_map<int, int>> local_maps_;
    
public:
    ThreadLocalAggregator(size_t num_threads) 
        : local_maps_(num_threads) {}
    
    void add(size_t thread_id, int key, int value) {
        local_maps_[thread_id][key] += value;
    }
    
    tsl::robin_map<int, int> merge() {
        tsl::robin_map<int, int> result;
        for (auto& local_map : local_maps_) {
            for (const auto& [key, value] : local_map) {
                result[key] += value;
            }
        }
        return result;
    }
};

// Usage
ThreadLocalAggregator aggregator(4);
std::vector<std::thread> workers;
for (size_t i = 0; i < 4; ++i) {
    workers.emplace_back([&aggregator, i]() {
        for (int j = 0; j < 1000; ++j) {
            aggregator.add(i, j % 100, 1);  // No locks needed
        }
    });
}
for (auto& t : workers) t.join();

auto final_result = aggregator.merge();  // Single-threaded merge
```