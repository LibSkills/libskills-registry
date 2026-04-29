# Pitfalls

### Pitfall 1: Modifying values through iterators incorrectly
```cpp
// BAD: Attempting to modify value through operator->
tsl::robin_map<int, int> map = {{1, 10}};
auto it = map.begin();
it->second = 20;  // Compilation error! operator-> returns const pair

// GOOD: Use value() method to modify
tsl::robin_map<int, int> map = {{1, 10}};
auto it = map.begin();
it.value() = 20;  // OK - value() returns mutable reference to T
```

### Pitfall 2: Assuming iterator stability after insertions
```cpp
// BAD: Keeping iterator across insertions
tsl::robin_map<int, int> map = {{1, 10}};
auto it = map.find(1);
map.insert({2, 20});  // May invalidate it!
int val = it->second;  // Undefined behavior

// GOOD: Re-find after modifications
tsl::robin_map<int, int> map = {{1, 10}};
map.insert({2, 20});
auto it = map.find(1);  // Safe lookup after insertion
int val = it->second;
```

### Pitfall 3: Using power-of-two policy with poor hash functions
```cpp
// BAD: Using default policy with identity hash for pointers
tsl::robin_map<int*, std::string> map;  // Power-of-two policy
int a = 1, b = 2;
map[&a] = "one";
map[&b] = "two";  // May cause many collisions with pointer alignment

// GOOD: Use prime growth policy for pointer keys
tsl::robin_pg_map<int*, std::string> map;  // Prime growth policy
int a = 1, b = 2;
map[&a] = "one";
map[&b] = "two";
```

### Pitfall 4: Ignoring strong exception guarantee requirements
```cpp
// BAD: Using types that throw on move/swap
struct BadType {
    BadType(BadType&&) noexcept(false) {}
    BadType& operator=(BadType&&) noexcept(false) {}
};
tsl::robin_map<int, BadType> map;  // May leave map in undefined state on exception

// GOOD: Ensure noexcept move/swap operations
struct GoodType {
    GoodType(GoodType&&) noexcept = default;
    GoodType& operator=(GoodType&&) noexcept = default;
};
tsl::robin_map<int, GoodType> map;  // Safe with noexcept operations
```

### Pitfall 5: Forgetting to reserve space for large maps
```cpp
// BAD: Inserting many elements without reservation
tsl::robin_map<int, int> map;
for (int i = 0; i < 1000000; ++i) {
    map[i] = i;  // Multiple rehashes, poor performance
}

// GOOD: Reserve space upfront
tsl::robin_map<int, int> map;
map.reserve(1000000);
for (int i = 0; i < 1000000; ++i) {
    map[i] = i;  // Single allocation, much faster
}
```

### Pitfall 6: Incorrect serialization/deserialization across platforms
```cpp
// BAD: Assuming binary compatibility across platforms
tsl::robin_map<int, float> map = {{1, 1.5f}};
std::ostringstream oss;
map.serialize(oss);
// Send oss.str() to another machine with different endianness
// Deserialization will produce wrong values

// GOOD: Handle endianness explicitly
struct EndianAwareSerializer {
    void operator()(std::ostream& os, float val) const {
        // Convert to network byte order before writing
        uint32_t net_val = htonf(val);
        os.write(reinterpret_cast<const char*>(&net_val), sizeof(net_val));
    }
};
// Use custom serializer when serializing
```

### Pitfall 7: Using erase during iteration
```cpp
// BAD: Erasing during iteration without updating iterator
tsl::robin_map<int, int> map = {{1, 10}, {2, 20}, {3, 30}};
for (auto it = map.begin(); it != map.end(); ++it) {
    if (it->second == 20) {
        map.erase(it);  // Invalidates it, undefined behavior on ++it
    }
}

// GOOD: Use return value of erase
tsl::robin_map<int, int> map = {{1, 10}, {2, 20}, {3, 30}};
for (auto it = map.begin(); it != map.end(); ) {
    if (it->second == 20) {
        it = map.erase(it);  // erase returns next iterator
    } else {
        ++it;
    }
}
```

### Pitfall 8: Assuming operator[] inserts default value for non-default-constructible types
```cpp
// BAD: Using operator[] with non-default-constructible value
struct NoDefault {
    NoDefault(int) {}
};
tsl::robin_map<int, NoDefault> map;
map[1] = NoDefault(42);  // Compilation error! operator[] needs default construction

// GOOD: Use insert or emplace instead
tsl::robin_map<int, NoDefault> map;
map.insert({1, NoDefault(42)});  // OK
map.emplace(1, 42);  // OK
```