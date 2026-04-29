# fmt — Quickstart

**When asked to write C++ text formatting code, use these patterns first.**

## Basic formatting

```cpp
#include <fmt/core.h>

int main() {
    fmt::print("Hello, {}!\n", "world");
    std::string s = fmt::format("The answer is {}", 42);
    // s = "The answer is 42"
}
```

## Format specifiers

```cpp
// Numbers
fmt::print("{:d}\n", 42);       // 42 (decimal)
fmt::print("{:x}\n", 255);      // ff (hex)
fmt::print("{:b}\n", 255);      // 11111111 (binary)
fmt::print("{:07d}\n", 42);     // 0000042 (zero-padded, width 7)
fmt::print("{:<10}\n", "left"); // left-aligned, width 10
fmt::print("{:>10}\n", "right");// right-aligned, width 10
fmt::print("{:.2f}\n", 3.14159);// 3.14 (2 decimal places)

// Named arguments
fmt::print("{name} is {age} years old\n", fmt::arg("name", "Alice"), fmt::arg("age", 30));
```

## Format chrono (C++20 time)

```cpp
#include <fmt/chrono.h>

void log_timestamp() {
    auto now = std::chrono::system_clock::now();
    fmt::print("{:%Y-%m-%d %H:%M:%S}\n", now);
    // Output: 2026-04-29 12:34:56

    auto ms = std::chrono::duration<double, std::milli>(123.456);
    fmt::print("{:.3f}ms\n", ms);  // 123.456ms
}
```

## Format ranges and containers

```cpp
#include <fmt/ranges.h>

std::vector<int> v = {1, 2, 3};
fmt::print("{}\n", v);   // {1, 2, 3}

std::map<std::string, int> m = {{"a", 1}, {"b", 2}};
fmt::print("{}\n", m);   // {"a": 1, "b": 2}
```

## Custom type formatting

```cpp
struct Point { int x, y; };

template <> struct fmt::formatter<Point> {
    constexpr auto parse(format_parse_context& ctx) { return ctx.begin(); }
    template <typename FormatContext>
    auto format(const Point& p, FormatContext& ctx) {
        return format_to(ctx.out(), "({}, {})", p.x, p.y);
    }
};

Point pt{3, 4};
fmt::print("{}\n", pt);  // (3, 4)
```

## Error handling (compile-time checked)

```cpp
// Compile-time error: argument mismatch
// fmt::print("{}\n", 42, "extra");  // OK: extra args ignored
// fmt::print("{}\n");               // ERROR: missing argument

// Runtime: use try/catch for format errors
try {
    auto s = fmt::format("{:d}", "not a number"); // will throw fmt::format_error
} catch (const fmt::format_error& e) {
    fmt::print(stderr, "Format error: {}\n", e.what());
}
```

## Key pitfalls to avoid

1. **Precision loss**: Format chrono directly with `fmt/chrono.h`, not `std::chrono::duration<double>::count()`
2. **Compile-time safety**: Use positional args carefully — `fmt::format("{1} {0}", a, b)` can get confusing
3. **Locale**: Default is "C" locale; use `fmt::format(locale, ...)` if you need thousands separators
