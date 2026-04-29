# Lifecycle

### Construction
```cpp
#include <tsl/robin_map.h>

// Default construction
tsl::robin_map<int, std::string> map1;

// Initializer list construction
tsl::robin_map<int, std::string> map2 = {{1, "one"}, {2, "two"}};

// Range construction
std::vector<std::pair<int, std::string>> vec = {{3, "three"}, {4, "four"}};
tsl::robin_map<int, std::string> map3(vec.begin(), vec.end());

// Copy construction
tsl::robin_map<int, std::string> map4(map2);

// Move construction
tsl::robin_map<int, std::string> map5(std::move(map4));
```

### Destruction and Resource Management
```cpp
// Automatic destruction - no special handling needed
{
    tsl::robin_map<int, std::string> map = {{1, "one"}};
    // map automatically destroys all elements when going out of scope
}

// Clear and reuse
tsl::robin_map<int, std::string> map = {{1, "one"}, {2, "two"}};
map.clear();  // Destroys all elements, keeps allocated memory
map[3] = "three";  // Reuses existing memory

// Release memory
tsl::robin_map<int, std::string> map = {{1, "one"}, {2, "two"}};
tsl::robin_map<int, std::string>().swap(map);  // Swap with empty map to release memory
```

### Move Semantics
```cpp
// Move assignment
tsl::robin_map<int, std::string> source = {{1, "one"}, {2, "two"}};
tsl::robin_map<int, std::string> dest;
dest = std::move(source);  // source is now empty

// Move with noexcept guarantee
static_assert(std::is_nothrow_move_constructible<tsl::robin_map<int, int>>::value,
              "Move construction should be noexcept");

// Move-only keys
tsl::robin_map<std::unique_ptr<int>, std::string> map;
auto key = std::make_unique<int>(42);
map.emplace(std::move(key), "answer");  // Move unique_ptr into map
```

### Resource Management with Custom Allocators
```cpp
// Using custom allocator for memory tracking
template<typename T>
struct TrackingAllocator : std::allocator<T> {
    using std::allocator<T>::allocator;
    
    T* allocate(std::size_t n) {
        std::cout << "Allocating " << n * sizeof(T) << " bytes\n";
        return std::allocator<T>::allocate(n);
    }
    
    void deallocate(T* p, std::size_t n) {
        std::cout << "Deallocating " << n * sizeof(T) << " bytes\n";
        std::allocator<T>::deallocate(p, n);
    }
};

using TrackedMap = tsl::robin_map<int, std::string, std::hash<int>,
                                   std::equal_to<int>, TrackingAllocator<std::pair<int, std::string>>>;

TrackedMap map;
map.reserve(100);  // Allocation tracked
map[1] = "one";    // Reuses existing memory
```

### Swap and Exchange
```cpp
// Swap contents efficiently
tsl::robin_map<int, std::string> map1 = {{1, "one"}, {2, "two"}};
tsl::robin_map<int, std::string> map2 = {{3, "three"}};

map1.swap(map2);  // O(1) swap of internal pointers

// Using std::swap
std::swap(map1, map2);  // Same efficiency
```