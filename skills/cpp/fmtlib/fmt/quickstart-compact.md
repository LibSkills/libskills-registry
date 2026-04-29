# fmt — Quick Start (Compact)

**Get started in 30 seconds.**

## Installation

```bash
# Header-only
git submodule add https://github.com/fmtlib/fmt.git extern/fmt

# Package managers
vcpkg install fmt
conan install fmt/11.0.2
```

## Basic Usage

```cpp
#include "fmt/core.h"
#include "fmt/ranges.h"

int main() {
    // Simple formatting
    fmt::print("Hello, {}!\n", "world");
    
    // Format with values
    int x = 42;
    fmt::print("Value: {}\n", x);
    
    // Format containers
    std::vector<int> vec = {1, 2, 3};
    fmt::print("Vector: {}\n", vec);
    
    // Format to string
    std::string result = fmt::format("Result: {}", 3.14);
    
    return 0;
}
```

## Compile

```bash
g++ -std=c++17 -o app main.cpp -Ifmt/include -Lfmt/build -lfmt
```

## Key Rules

1. ✅ Use `{}` for formatting (not `%s`)
2. ✅ Use `FMT_STRING()` for compile-time check (C++17)
3. ✅ Use `fmt::format()` for string results
4. ❌ Don't use user-controlled format strings
5. ❌ Don't use `fmt::format_to` with small buffers

## Common Patterns

```cpp
// Named arguments
fmt::print("{name} is {age} years old\n", fmt::arg("name", "John"), fmt::arg("age", 30));

// Alignment and padding
fmt::print("{:<10}\n", "left");    // left-aligned
fmt::print("{:>10}\n", "right");   // right-aligned
fmt::print("{:^10}\n", "center");  // center-aligned

// Formatting numbers
fmt::print("{:.2f}\n", 3.14159);   // 2 decimal places
fmt::print("{:08d}\n", 42);        // zero-padded
```

## Next Steps

- Read `pitfalls.md` for common mistakes
- Read `safety.md` for critical rules
- Read `performance.md` for optimization tips

**Need help?** Run `libskills get cpp/fmtlib/fmt` to download full skill.