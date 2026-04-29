# Performance

### Performance Characteristics
```cpp
// Robin-map typically outperforms std::unordered_map
#include <chrono>
#include <iostream>

void benchmark_lookup() {
    constexpr int N = 1000000;
    
    tsl::robin_map<int, int> robin_map;
    std::unordered_map<int, int> std_map;
    
    // Fill both maps
    for (int i = 0; i < N; ++i) {
        robin_map[i] = i;
        std_map[i] = i;
    }
    
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < N; ++i) {
        volatile auto val = robin_map.find(i);
    }
    auto robin_time = std::chrono::high_resolution_clock::now() - start;
    
    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < N; ++i) {
        volatile auto val = std_map.find(i);
    }
    auto std_time = std::chrono::high_resolution_clock::now() - start;
    
    std::cout << "Robin-map: " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(robin_time).count()
              << "ms\n";
    std::cout << "std::unordered_map: "
              << std::chrono::duration_cast<std::chrono::milliseconds>(std_time).count()
              << "ms\n";
}
```

### Allocation Patterns and Optimization
```cpp
// Minimize rehashes by reserving capacity
tsl::robin_map<int, int> map;

// BAD: Multiple rehashes
for (int i = 0; i < 1000000; ++i) {
    map[i] = i;  // May cause ~20 rehashes
}

// GOOD: Single allocation
tsl::robin_map<int, int> optimized_map;
optimized_map.reserve(1000000);
for (int i = 0; i < 1000000; ++i) {
    optimized_map[i] = i;  // No rehashes
}
```

### Cache-Friendly Access Patterns
```cpp
// Robin-map's open-addressing provides better cache locality
struct ExpensiveObject {
    int data[64];  // Large object
};

// BAD: Iterating and modifying large objects
tsl::robin_map<int, ExpensiveObject> map;
for (int i = 0; i < 1000; ++i) {
    map[i] = ExpensiveObject{};
}

// GOOD: Store pointers for large objects to improve cache performance
tsl::robin_map<int, std::unique_ptr<ExpensiveObject>> ptr_map;
for (int i = 0; i < 1000; ++i) {
    ptr_map[i] = std::make_unique<ExpensiveObject>();
}
```

### Precalculated Hash Optimization
```cpp
// Use precalculated hash for repeated lookups
tsl::robin_map<std::string, int> map;
map["key1"] = 1;
map["key2"] = 2;

// BAD: Computing hash each time
for (int i = 0; i < 1000; ++i) {
    auto it = map.find("key1");  // Hash computed 1000 times
}

// GOOD: Compute hash once
std::size_t hash = map.hash_function()("key1");
for (int i = 0; i < 1000; ++i) {
    auto it = map.find("key1", hash);  // Uses precomputed hash
}
```

### Memory Usage Optimization
```cpp
// StoreHash can reduce memory in some cases
// When StoreHash is true, hash is stored alongside key-value
// This can speed up rehashing but uses more memory

// BAD: Using StoreHash when not needed
tsl::robin_map<int, int, std::hash<int>, std::equal_to<int>,
               std::allocator<std::pair<int, int>>, true> map;  // Extra memory for hash

// GOOD: Let library decide based on alignment
tsl::robin_map<int, int> map;  // Library may store hash if no memory impact
```

### Batch Operations
```cpp
// Batch insertions are more efficient than individual ones
std::vector<std::pair<int, int>> batch_data;
batch_data.reserve(1000000);
for (int i = 0; i < 1000000; ++i) {
    batch_data.emplace_back(i, i * 2);
}

// BAD: Individual insertions
tsl::robin_map<int, int> map1;
for (const auto& [key, value] : batch_data) {
    map1[key] = value;  // Multiple rehashes
}

// GOOD: Batch insertion with reserve
tsl::robin_map<int, int> map2;
map2.reserve(batch_data.size());
for (const auto& [key, value] : batch_data) {
    map2[key] = value;  // Single allocation
}
```