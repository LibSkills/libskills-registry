# spdlog — Quick Start (Compact)

**Get started in 30 seconds.**

## Installation

```bash
# Header-only (just include)
git submodule add https://github.com/gabime/spdlog.git extern/spdlog

# Or package managers
vcpkg install spdlog
conan install spdlog/1.14.2
```

## Basic Usage

```cpp
#include "spdlog/spdlog.h"
#include "spdlog/sinks/rotating_file_sink.h"

int main() {
    // Create logger (1MB max, 3 files)
    auto logger = spdlog::rotating_logger_mt("app", "logs/app.log", 1048576, 3);
    
    // Log messages
    logger->info("Application started");
    logger->debug("User {} logged in", "john");
    logger->warn("Disk usage: {}%", 85);
    logger->error("Failed to connect to database");
    
    // Shutdown (REQUIRED!)
    spdlog::shutdown();
    return 0;
}
```

## Compile

```bash
g++ -std=c++17 -o app main.cpp -I/path/to/spdlog/include
```

## Key Rules

1. ✅ Use `_mt` suffix for thread safety
2. ✅ Call `spdlog::shutdown()` in main()
3. ✅ Use `{}` for formatting, not `+`
4. ❌ Don't log in static destructors
5. ❌ Don't use `std::endl`

## Next Steps

- Read `pitfalls.md` for common mistakes
- Read `safety.md` for critical rules
- Read `threading.md` for multi-threaded usage

**Need help?** Run `libskills get cpp/gabime/spdlog` to download full skill.