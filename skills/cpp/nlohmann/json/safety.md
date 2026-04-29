# nlohmann/json — Safety

Red lines — conditions that must NEVER occur.

## NEVER use operator[] on a const json for a missing key

`const json::operator[]` does NOT insert a null — it throws `json::out_of_range`.

```cpp
// NEVER
const json j = {{"a", 1}};
int x = j["b"]; // ❌ throws json::out_of_range

// ALWAYS: check first
if (j.contains("b")) {
    int x = j["b"];
}

// ALWAYS: use value() with default
int x = j.value("b", 0);
```

## NEVER parse untrusted input without exception handling

Malformed JSON unconditionally throws. Without a try/catch, any user-provided JSON can crash the process.

```cpp
// NEVER
json j = json::parse(user_input); // uncaught exception on bad input

// ALWAYS
try {
    json j = json::parse(user_input);
} catch (const json::parse_error& e) {
    // handle gracefully
}
```

## NEVER store pointers or references to elements that may invalidate

Insertion, erasure, and swap operations can invalidate references and iterators into a `json` value.

```cpp
// NEVER
json arr = json::array({1, 2, 3});
int* p = &arr[0].get_ref<int&>(); // pointer into internal storage
arr.push_back(4);                 // p may be dangling

// ALWAYS: copy instead
int val = arr[0].get<int>();
```

## NEVER assume thread safety for writes

`json` has no internal synchronization. Concurrent writes from multiple threads is a data race.

```cpp
// NEVER — data race
json j;
std::thread t1([&]{ j["a"] = 1; });
std::thread t2([&]{ j["b"] = 2; });
t1.join(); t2.join();

// ALWAYS: use mutex
std::mutex mtx;
json j;
std::thread t1([&]{
    std::lock_guard<std::mutex> lock(mtx);
    j["a"] = 1;
});
std::thread t2([&]{
    std::lock_guard<std::mutex> lock(mtx);
    j["b"] = 2;
});
t1.join(); t2.join();
```

## NEVER use `dump()` with indent on output that will be consumed by parser (wire format)

Indented output is larger and slower to parse. Use compact (default) dump for API responses, indented for logs/files.

```cpp
// NEVER for API responses
response.body = j.dump(4); // 4-space indent — wastes bandwidth

// ALWAYS for API/network
response.body = j.dump(); // compact, no whitespace

// For human-readable files
file << j.dump(2);
```
