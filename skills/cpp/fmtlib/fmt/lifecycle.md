# fmt — Lifecycle

## Header-Only vs Compiled

```cpp
// Header-only (default)
#include <fmt/core.h>

// Compiled library (faster builds)
#define FMT_HEADER_ONLY
// or link against -lfmt
```

## Initialization

No initialization required. fmt is stateless. The first call to any `fmt::` function triggers static initialization of internal tables (thread-safe, one-time cost).

## Custom Formatters

```cpp
#include <fmt/format.h>

struct Point { int x, y; };

template <> struct fmt::formatter<Point> {
    constexpr auto parse(format_parse_context& ctx) { return ctx.begin(); }
    auto format(const Point& p, format_context& ctx) {
        return fmt::format_to(ctx.out(), "({}, {})", p.x, p.y);
    }
};
// Usage: fmt::format("{}", Point{1, 2}) → "(1, 2)"
```

## Locale Support

```cpp
#include <fmt/format.h>
#include <fmt/locale.h>

// Use system locale for formatting
std::locale::global(std::locale("en_US.UTF-8"));
fmt::print("{:L}\n", 1234567); // "1,234,567" (locale-dependent thousands separator)
```

## Color Output

```cpp
#include <fmt/color.h>

fmt::print(fg(fmt::color::steel_blue) | fmt::emphasis::bold, "Hello, {}!\n", "World");
fmt::print(fg(fmt::terminal_color::red), "Error: {}\n", "something went wrong");
```
