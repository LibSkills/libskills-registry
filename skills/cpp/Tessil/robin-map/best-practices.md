# Best Practices

### Reserve capacity for known sizes
```cpp
// Best practice: Pre-allocate when you know the size
tsl::robin_map<int, std::string> map;
map.reserve(10000);  // Single allocation upfront
for (int i = 0; i < 10000; ++i) {
    map[i] = std::to_string(i);
}
```

### Use prime growth policy for pointer keys or poor hash functions
```cpp
// Best practice: Choose growth policy based on key type
// For pointers or integer keys with patterns in lower bits
tsl::robin_pg_map<MyClass*, int> pointer_map;

// For general use with good hash functions
tsl::robin_map<std::string, int> string_map;
```

### Prefer emplace over insert for efficiency
```cpp
// Best practice: Use emplace to avoid unnecessary copies
tsl::robin_map<int, std::string> map;

// Efficient: Constructs in-place
map.emplace(1, "one");

// Less efficient: Creates temporary pair, then moves
map.insert(std::make_pair(2, "two"));
```

### Use heterogeneous lookup for string keys
```cpp
// Best practice: Use string_view for lookups to avoid string construction
tsl::robin_map<std::string, int, std::hash<std::string>, 
               std::equal_to<>> map;  // Transparent comparator
map["hello"] = 1;

std::string_view sv = "hello";
auto it = map.find(sv);  // No std::string construction
```

### Store hash for expensive hash functions
```cpp
// Best practice: Store hash when hash function is expensive
struct ExpensiveHash {
    std::size_t operator()(const std::string& s) const {
        // Some expensive hash computation
        std::this_thread::sleep_for(std::chrono::microseconds(100));
        return std::hash<std::string>{}(s);
    }
};

// Store hash to avoid recomputation during rehash
tsl::robin_map<std::string, int, ExpensiveHash, 
               std::equal_to<std::string>, 
               std::allocator<std::pair<std::string, int>>,
               true> map;  // StoreHash = true
```

### Use precalculated hash for repeated lookups
```cpp
// Best practice: Cache hash for repeated lookups of same key
tsl::robin_map<int, std::string> map = {{1, "one"}, {2, "two"}};

std::size_t hash = map.hash_function()(1);
// Multiple lookups with same key
auto it1 = map.find(1, hash);
auto it2 = map.find(1, hash);  // Faster with precalculated hash
```

### Handle erase during iteration correctly
```cpp
// Best practice: Use erase return value for safe iteration
tsl::robin_map<int, int> map = {{1, 10}, {2, 20}, {3, 30}};

for (auto it = map.begin(); it != map.end(); ) {
    if (it->second % 2 == 0) {
        it = map.erase(it);  // erase returns next iterator
    } else {
        ++it;
    }
}
```

### Use serialization for state persistence
```cpp
// Best practice: Serialize for saving/loading map state
tsl::robin_map<int, std::string> map = {{1, "one"}, {2, "two"}};

// Save to file
std::ofstream ofs("map_data.bin", std::ios::binary);
map.serialize(ofs);

// Load from file
tsl::robin_map<int, std::string> loaded_map;
std::ifstream ifs("map_data.bin", std::ios::binary);
loaded_map.deserialize(ifs);
```