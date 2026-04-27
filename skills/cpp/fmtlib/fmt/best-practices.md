# fmt — Best Practices

## Use compile-time format string checking

```cpp
// C++20: std::format is compile-time checked
#include <format>
auto s = std::format("Hello, {}!", name);

// C++17: FMT_STRING macro for compile-time checking
#include <fmt/format.h>
auto s = fmt::format(FMT_STRING("Hello, {}!"), name);

// BAD: no compile-time checking — possible runtime error
auto s = fmt::format(runtime_format_str, args...);
```

## Prefer fmt::format over string streams

```cpp
// BAD: verbose, slow, allocation-heavy
std::stringstream ss;
ss << "User " << id << ": " << name << " (" << email << ")";
auto result = ss.str();

// GOOD: concise, fast, single allocation
auto result = fmt::format("User {}: {} ({})", id, name, email);
```

## Use fmt::join for containers

```cpp
std::vector<int> v = {1, 2, 3, 4, 5};
fmt::print("[{}]\n", fmt::join(v, ", ")); // [1, 2, 3, 4, 5]
```

## Use fmt::format_to for buffer reuse

```cpp
std::string buffer;
buffer.reserve(1024);
for (const auto& item : items) {
    buffer.clear();
    fmt::format_to(std::back_inserter(buffer), "Item: {}\n", item);
    process(buffer);
}
```

## Named arguments for clarity

```cpp
// Indexed: easy to swap arguments
fmt::print("User {1} has email {0}\n", email, username);

// Named: self-documenting
fmt::print("User {name} has email {email}\n",
    fmt::arg("name", username), fmt::arg("email", email));
```

## Custom formatting for user types

```cpp
struct Money { int64_t cents; };

template <> struct fmt::formatter<Money> {
    constexpr auto parse(format_parse_context& ctx) -> decltype(ctx.begin()) {
        auto it = ctx.begin();
        if (it != ctx.end() && *it == '}') return it;
        throw format_error("invalid format");
    }
    auto format(const Money& m, format_context& ctx) {
        return fmt::format_to(ctx.out(), "${}.{:02}",
            m.cents / 100, std::abs(m.cents % 100));
    }
};
```
