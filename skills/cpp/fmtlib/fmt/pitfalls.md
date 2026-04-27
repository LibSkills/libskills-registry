# fmt — Pitfalls

## Do NOT pass user-controlled format strings

fmt interprets format strings at runtime (unless using compile-time checking). An attacker-controlled format string can read arbitrary stack memory, cause crashes with invalid specifiers, or leak information.

```cpp
// BAD: format string injection
std::string user_name = req.get_param("name");
fmt::print(user_name, 42); // user_name = "{}" → reads stack

// GOOD: fixed format string
fmt::print("User: {}", user_name);
```

## Do NOT mix printf-style format specifiers

fmt uses `{}` syntax (Python-like), not `%s`/`%d` (printf). Using `%s` prints a literal `%s`.

```cpp
// BAD: prints "Value: %s" literally
fmt::print("Value: %s", 42);

// GOOD
fmt::print("Value: {}", 42);
```

## Do NOT lose compile-time checking with dynamic format strings

In C++17 mode (no `std::format`), compile-time checking requires `FMT_STRING()` macro. Without it, type errors become runtime exceptions.

```cpp
// BAD: compiles but throws at runtime
fmt::format("Value: {}", "hello"); // ok
fmt::format("Value: {:d}", "hello"); // RUNTIME error — {:d} expects int

// GOOD: compile error in C++17
fmt::format(FMT_STRING("Value: {:d}"), "hello"); // COMPILE ERROR

// GOOD: C++20 std::format — compile-time checked by default
std::format("Value: {:d}", "hello"); // COMPILE ERROR
```

## Do NOT use `fmt::format_to` with undersized buffers

`fmt::format_to` writes to an output iterator. If the destination is a fixed-size buffer, overflow is undefined behavior.

```cpp
// BAD: buffer overflow
char buf[10];
fmt::format_to(buf, "{}", "this string is very long"); // UB!

// GOOD: use fmt::format (returns std::string)
auto result = fmt::format("{}", "this string is very long");
```

## Do NOT pass temporary `fmt::format` results to functions expecting `const char*`

`fmt::format()` returns `std::string`. `.c_str()` on a temporary is valid only within the full expression.

```cpp
// BAD: dangling pointer
const char* msg = fmt::format("Hello, {}!", name).c_str(); // temporary destroyed
printf("%s", msg); // undefined behavior

// GOOD: keep string alive
std::string msg = fmt::format("Hello, {}!", name);
printf("%s", msg.c_str());
```

## Do NOT use `fmt::join` with ranges that return references to temporaries

```cpp
// BAD: dangling reference
auto joined = fmt::join(
    vec | std::views::transform([](int i) { return std::to_string(i); }),
    ", "
); // temporary strings destroyed — UB when joined is used
```
