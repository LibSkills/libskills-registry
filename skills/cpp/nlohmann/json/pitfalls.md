# nlohmann/json — Pitfalls

Common mistakes that cause crashes, data loss, or silent corruption.

## Do NOT access a missing key without checking

Accessing a missing key with `operator[]` on a `const json` throws `json::out_of_range`. On a non-const `json`, it inserts a `null` value silently (and then returns it).

```cpp
// BAD: non-const operator[] creates null entry silently
json j;
int x = j["nonexistent"]; // inserts j["nonexistent"] = null, then throws

// GOOD: use contains() or find() first
if (j.contains("key")) {
    auto& v = j["key"];
}

// GOOD: use value() with default
int x = j.value("key", 42); // returns 42 if key missing

// GOOD: use find()
auto it = j.find("key");
if (it != j.end()) {
    int x = it->get<int>();
}
```

## Do NOT store references to `json` elements — they invalidate on insertion

JSON is a tree of `std::unique_ptr` nodes internally. Inserting elements can reallocate and invalidate all references and pointers.

```cpp
// BAD: dangling reference after insertion
json arr = json::array({1, 2, 3});
int& ref = arr[0].get_ref<int&>(); // reference to internal storage
arr.push_back(4);                   // ❌ may reallocate — ref is dangling

// GOOD: use copies, not references
int val = arr[0].get<int>();
arr.push_back(4);
// val is safe

// GOOD: use iterator if you must, but don't insert while iterating
for (auto it = arr.begin(); it != arr.end(); ++it) {
    // do NOT call arr.insert/arr.push_back here
}
```

## Do NOT parse untrusted input without try/catch

All parse errors throw. A malformed JSON string from user input will crash an unprotected program.

```cpp
// BAD: crashes on malformed input
std::string input = get_user_input();
json j = json::parse(input); // ❌ throws if input is not valid JSON

// GOOD: catch parse errors
try {
    json j = json::parse(input);
} catch (const json::parse_error& e) {
    log("Parse failed: {}", e.what());
}

// ALSO GOOD: use accepting parser with ignore_comments
json j = json::parse(input, nullptr, true, true); // allow exceptions + comments
```

## Do NOT assume `dump()` preserves insertion order with `json`

`json` uses `std::map` (ordered by key), so keys are sorted alphabetically. Use `nlohmann::ordered_json` to preserve insertion order.

```cpp
// BAD: keys reordered alphabetically
json j;
j["zebra"] = 1;
j["apple"] = 2;
std::cout << j.dump(); // {"apple":2,"zebra":1} — keys are sorted!

// GOOD: use ordered_json
nlohmann::ordered_json oj;
oj["zebra"] = 1;
oj["apple"] = 2;
std::cout << oj.dump(); // {"zebra":1,"apple":2}
```

## Do NOT use `get<int>()` on a value that may be a float

Type mismatch throws `json::type_error`. A JSON number `3.14` cannot be `get<int>()`.

```cpp
// BAD: throws type_error
json j = 3.14;
int x = j.get<int>(); // ❌ 3.14 is a float, not int

// GOOD: check type first
if (j.is_number_integer()) {
    int x = j.get<int>();
} else if (j.is_number_float()) {
    double d = j.get<double>();
    int x = static_cast<int>(d); // explicit cast
}

// ALSO GOOD: use get<double>() and let narrowing happen explicitly
double d = j.get<double>();
int x = static_cast<int>(d);
```

## Do NOT copy large JSON objects when passing to functions

`json` uses shared-ownership internally, but non-const access forces a deep copy. Pass by `const&` for readonly access.

```cpp
// BAD: deep copy on every function call
void process(json j) { // ❌ copies entire tree
    std::cout << j.dump();
}

// GOOD: const reference — no copy
void process(const json& j) {
    std::cout << j.dump();
}

// GOOD: move when you're done with the source
void consume(json&& j) {
    std::cout << j.dump();
    // j is valid but unspecified after
}
```
