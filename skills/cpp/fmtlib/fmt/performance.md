# fmt — Performance

## Throughput (approximate, modern x86_64)

| Method | Operations/sec | vs printf |
|--------|---------------|-----------|
| `fmt::format` | ~200M/s | 2-5x faster |
| `fmt::format_to` (pre-allocated) | ~300M/s | 5-10x faster |
| `printf` | ~80M/s | baseline |
| `std::stringstream` | ~10M/s | 8-20x slower |

## Performance Rules

- **fmt::format_to >> fmt::format**: avoid allocation when you have a buffer
- **Compile-time format strings are faster**: runtime format parsing has non-trivial overhead
- **fmt::join is faster than manual loops**: optimized buffer allocation
- **Avoid locale formatting unless needed**: `{:L}` triggers locale lookups
- **Use fmt::memory_buffer for stack-allocated temporary strings** (up to 500 chars on stack)

## Avoid Unnecessary Allocations

```cpp
// BAD: multiple allocations (format + concatenation)
auto msg = fmt::format("Error {}: {}", code, "msg");
auto full = fmt::format("[{}] {}", timestamp, msg);

// GOOD: single allocation
auto full = fmt::format("[{}] Error {}: {}", timestamp, code, "msg");
```

## Use fmt::memory_buffer for Hot Paths

```cpp
fmt::memory_buffer buf;
for (int i = 0; i < 1'000'000; i++) {
    buf.clear();
    fmt::format_to(std::back_inserter(buf), "Item: {}\n", i);
    process({buf.data(), buf.size()});
}
```

## fmt vs std::format

| Aspect | fmt 11 | std::format (C++20) |
|--------|--------|---------------------|
| Speed | Fastest | Same backend (fmt) |
| Features | Full (color, join, named args) | Basic |
| Header-only | Optional | No |
| C++17 support | Yes | No |
