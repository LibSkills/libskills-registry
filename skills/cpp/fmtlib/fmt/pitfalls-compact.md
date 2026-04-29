# fmt — Pitfalls (Compact)

**Critical mistakes to avoid. Read this before generating fmt code.**

## 1. Format String Injection ❌→✅

```cpp
// BAD: user-controlled format string (security risk)
std::string user_input = get_user_input();
fmt::print(user_input, 42);  // Attacker can read stack!

// GOOD: fixed format string
fmt::print("User: {}", user_input);
```

## 2. Wrong Format Syntax ❌→✅

```cpp
// BAD: printf-style (prints literal "%s")
fmt::print("Value: %s", 42);

// GOOD: Python-style
fmt::print("Value: {}", 42);
```

## 3. Missing Compile-Time Check ❌→✅

```cpp
// BAD: runtime error in C++17
fmt::format("Value: {:d}", "hello");  // Throws exception!

// GOOD: compile-time check
fmt::format(FMT_STRING("Value: {:d}"), "hello");  // Compile error!

// BETTER: C++20 std::format (auto checked)
std::format("Value: {:d}", "hello");  // Compile error!
```

## 4. Buffer Overflow ❌→✅

```cpp
// BAD: buffer overflow
char buf[10];
fmt::format_to(buf, "{}", "very long string");  // UB!

// GOOD: use std::string
auto result = fmt::format("{}", "very long string");
```

## 5. Dangling Pointer ❌→✅

```cpp
// BAD: dangling pointer
const char* msg = fmt::format("Hello, {}!", name).c_str();
printf("%s", msg);  // UB!

// GOOD: keep string alive
std::string msg = fmt::format("Hello, {}!", name);
printf("%s", msg.c_str());
```

## 6. Temporary References ❌→✅

```cpp
// BAD: dangling reference
auto joined = fmt::join(
    vec | std::views::transform([](int i) { return std::to_string(i); }),
    ", "
);  // Temporary strings destroyed!

// GOOD: store temporaries
auto strings = vec | std::views::transform([](int i) { return std::to_string(i); });
auto joined = fmt::join(strings, ", ");
```

**Summary**: Use `{}` syntax, fixed format strings, and `FMT_STRING()` for safety.