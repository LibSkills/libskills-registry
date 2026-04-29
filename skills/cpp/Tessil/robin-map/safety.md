# Safety

### Red Line 1: NEVER use with types that throw on move/swap without understanding the consequences
```cpp
// BAD: Using throwing move constructor
struct ThrowingMove {
    ThrowingMove(ThrowingMove&&) noexcept(false) {}
};
tsl::robin_map<int, ThrowingMove> map;  // DANGER: Exception may leave map in undefined state

// GOOD: Ensure noexcept or use copy-only types
struct SafeType {
    SafeType(const SafeType&) = default;
    SafeType(SafeType&&) noexcept = default;
};
tsl::robin_map<int, SafeType> map;  // SAFE: noexcept operations
```

### Red Line 2: NEVER access elements after modifying operations without re-finding
```cpp
// BAD: Using iterator after insertion
tsl::robin_map<int, int> map = {{1, 10}};
auto it = map.find(1);
map.insert({2, 20});  // May invalidate all iterators
int val = it->second;  // DANGER: Undefined behavior

// GOOD: Always re-find after modifications
tsl::robin_map<int, int> map = {{1, 10}};
map.insert({2, 20});
auto it = map.find(1);  // SAFE: Fresh lookup
int val = it->second;
```

### Red Line 3: NEVER use operator[] with non-default-constructible value types
```cpp
// BAD: operator[] requires default construction
struct NonDefault {
    NonDefault() = delete;
    NonDefault(int) {}
};
tsl::robin_map<int, NonDefault> map;
map[1] = NonDefault(42);  // DANGER: Compilation error or undefined behavior

// GOOD: Use insert or emplace
tsl::robin_map<int, NonDefault> map;
map.emplace(1, 42);  // SAFE: Constructs in-place
```

### Red Line 4: NEVER assume thread safety for concurrent writes
```cpp
// BAD: Concurrent writes from multiple threads
tsl::robin_map<int, int> map;
std::vector<std::thread> threads;
for (int i = 0; i < 10; ++i) {
    threads.emplace_back([&map, i]() {
        map[i] = i;  // DANGER: Data race on concurrent writes
    });
}

// GOOD: Use external synchronization
tsl::robin_map<int, int> map;
std::mutex mtx;
std::vector<std::thread> threads;
for (int i = 0; i < 10; ++i) {
    threads.emplace_back([&map, &mtx, i]() {
        std::lock_guard<std::mutex> lock(mtx);
        map[i] = i;  // SAFE: Protected by mutex
    });
}
```

### Red Line 5: NEVER serialize/deserialize across platforms with different binary representations without custom serializers
```cpp
// BAD: Cross-platform serialization without endianness handling
tsl::robin_map<int, double> map = {{1, 3.14}};
std::ostringstream oss;
map.serialize(oss);
// Send to big-endian machine - DANGER: Wrong values on deserialization

// GOOD: Handle platform differences explicitly
struct PortableSerializer {
    void operator()(std::ostream& os, double val) const {
        uint64_t net_val = htond(val);  // Convert to network byte order
        os.write(reinterpret_cast<const char*>(&net_val), sizeof(net_val));
    }
    void operator()(std::istream& is, double& val) const {
        uint64_t net_val;
        is.read(reinterpret_cast<char*>(&net_val), sizeof(net_val));
        val = ntohd(net_val);  // Convert from network byte order
    }
};
// Use custom serializer for portable serialization
```