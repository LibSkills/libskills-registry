# fmt — Threading

**fmt is fully thread-safe.** All formatting functions are safe to call from multiple threads concurrently.

## Thread Safety Guarantees

- `fmt::format`, `fmt::print`, `fmt::format_to` — all thread-safe
- Internal format string caching uses lock-free data structures
- No mutable global state after static initialization
- Custom formatters MUST be thread-safe (no mutable static state)

## Custom Formatter Thread Safety

```cpp
// GOOD: stateless formatter — thread-safe
template <> struct fmt::formatter<MyType> {
    auto format(const MyType& v, format_context& ctx) {
        return fmt::format_to(ctx.out(), "{}", v.name);
    }
};

// BAD: mutable state — data race
template <> struct fmt::formatter<MyType> {
    static int counter; // shared mutable state
    auto format(const MyType& v, format_context& ctx) {
        return fmt::format_to(ctx.out(), "{}(#{})", v.name, ++counter);
    }
};
```

## Memory Allocation

- `fmt::format` allocates a `std::string` — thread-safe (allocator is thread-safe)
- `fmt::memory_buffer` — grows on the stack, no allocation for small strings
- `fmt::format_to` with existing buffer — no allocation, completely thread-safe

## Compile-Time vs Runtime

- Format string compilation (C++20 `std::format` / `FMT_STRING`) happens at compile time — zero threading concerns
- Runtime format strings are parsed on each call — parsing is thread-safe but slower under contention
