# Quickstart

```cpp
#include <tsl/robin_map.h>
#include <tsl/robin_set.h>
#include <iostream>
#include <string>

// Basic usage patterns for tsl::robin_map and tsl::robin_set

// Pattern 1: Construction and insertion
void basic_usage() {
    tsl::robin_map<int, std::string> map;
    map.insert({1, "one"});
    map[2] = "two";
    map.emplace(3, "three");
    
    tsl::robin_set<int> set;
    set.insert(10);
    set.insert(20);
}

// Pattern 2: Lookup with find
void lookup_example() {
    tsl::robin_map<int, std::string> map = {{1, "one"}, {2, "two"}};
    
    auto it = map.find(1);
    if (it != map.end()) {
        std::cout << "Found: " << it->second << std::endl;
    }
}

// Pattern 3: Iterating and modifying values
void iterate_and_modify() {
    tsl::robin_map<int, int> map = {{1, 10}, {2, 20}, {3, 30}};
    
    for (auto it = map.begin(); it != map.end(); ++it) {
        it.value() += 5;  // Use value() to modify
    }
}

// Pattern 4: Heterogeneous lookup (C++20)
void heterogeneous_lookup() {
    tsl::robin_map<std::string, int> map = {{"hello", 1}, {"world", 2}};
    
    // Use string_view without constructing std::string
    std::string_view sv = "hello";
    auto it = map.find(sv);
    if (it != map.end()) {
        std::cout << it->second << std::endl;
    }
}

// Pattern 5: Serialization
void serialization_example() {
    tsl::robin_map<int, std::string> map = {{1, "one"}, {2, "two"}};
    
    // Serialize to a stream
    std::ostringstream oss;
    map.serialize(oss);
    
    // Deserialize
    tsl::robin_map<int, std::string> restored;
    std::istringstream iss(oss.str());
    restored.deserialize(iss);
}

// Pattern 6: Precalculated hash
void precalculated_hash_example() {
    tsl::robin_map<int, std::string> map = {{1, "one"}, {2, "two"}};
    
    std::size_t hash_value = map.hash_function()(1);
    auto it = map.find(1, hash_value);
    if (it != map.end()) {
        std::cout << "Found with precalculated hash" << std::endl;
    }
}

// Pattern 7: Using prime growth policy for better hash distribution
void prime_growth_policy() {
    tsl::robin_pg_map<int, std::string> map;  // Uses prime growth policy
    map[1] = "one";
    map[2] = "two";
}

// Pattern 8: Storing hash for faster rehash
void store_hash_example() {
    // StoreHash<true> stores hash alongside key-value
    tsl::robin_map<int, std::string, std::hash<int>, 
                   std::equal_to<int>, std::allocator<std::pair<int, std::string>>,
                   true> map;
    map[1] = "one";
}
```