# fmt — Safety

Red lines — conditions that must NEVER occur.

## NEVER pass user-controlled data as the format string

Format string injection is a security vulnerability. An attacker who controls the format string can:
- Read arbitrary stack memory with `%s` or `{}`
- Crash the program with invalid format specifiers
- Leak sensitive data from the stack

```cpp
// NEVER: format string injection
void log_user_input(const std::string& user_msg) {
    fmt::print(user_msg); // user_msg = "{}" leaks stack data
}

// ALWAYS: fixed format strings
void log_user_input(const std::string& user_msg) {
    fmt::print("User message: {}", user_msg);
}
```

## NEVER use `fmt::format_to` on raw char arrays without bounds checking

Writing past the end of a stack-allocated buffer is a buffer overflow — classic memory corruption, exploitable.

```cpp
// NEVER: no bounds checking
char buf[32];
fmt::format_to(buf, "User input: {}", untrusted_input); // may overflow

// ALWAYS: use fmt::format for dynamic allocation
std::string result = fmt::format("User input: {}", untrusted_input);
```

## NEVER use runtime format strings without exception handling

fmt throws `fmt::format_error` on invalid format strings or type mismatches (C++17 mode without `FMT_STRING`). An uncaught exception crashes the program.

```cpp
// C++17: wrap in try-catch if format string is dynamic
try {
    auto result = fmt::format(dynamic_fmt_str, args...);
} catch (const fmt::format_error& e) {
    // handle gracefully
}
```

## NEVER specialize `fmt::formatter<T>` with mutable state

Formatters should be pure functions. A formatter with mutable state is not thread-safe and produces non-deterministic output when called concurrently from multiple threads.

```cpp
// NEVER: formatter with mutable state
template <> struct fmt::formatter<MyType> {
    static int counter; // shared mutable state — data race
    auto format(const MyType& v, format_context& ctx) {
        return fmt::format_to(ctx.out(), "{}#{}", v.name, ++counter);
    }
};
```
