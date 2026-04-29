# nlohmann/json — Performance

## Throughput (approximate, modern x86_64, single thread)

| Operation | Throughput | Notes |
|-----------|-----------|-------|
| Parse 1KB of JSON | ~500K ops/s | ~500 MB/s |
| Parse 100KB of JSON | ~10K ops/s | ~1 GB/s |
| Dump 1KB of JSON | ~1M ops/s | ~1 GB/s |
| Dump 100KB of JSON | ~15K ops/s | ~1.5 GB/s |
| Access known key | ~10M ops/s | O(log n) map lookup |
| SAX parse 1MB file | ~3x faster than tree parse | Avoids allocation + tree build |

## Comparisons

| Library | Parse 10MB JSON | Memory for 10MB JSON | Header size |
|---------|----------------|---------------------|-------------|
| nlohmann/json | ~30ms | ~50-80MB | ~500KB (single header) |
| RapidJSON (in-situ) | ~8ms | ~15-25MB | ~200KB |
| simdjson | ~3ms | ~10MB | ~100KB |

nlohmann/json is **ergonomic but not the fastest**. Use simdjson or RapidJSON when throughput >100MB/s is required.

## Performance Rules

- **Use SAX for large files**: `sax_parse()` avoids building the entire DOM tree; memory usage is O(depth) instead of O(file_size)
- **Reuse `json` objects** to avoid repeated allocation/deallocation. Clear with `j.clear()` instead of destroying and recreating
- **Prefer `value()` over `contains()` + `operator[]`**: `value()` does one lookup; `contains()` + `operator[]` does two
- **Avoid deep copying**: pass `const json&` to functions; use `std::move` when transferring ownership
- **Use compact serialization** for network: `j.dump()` (no indent) is 2-5x faster than `j.dump(4)`
- **Binary formats (CBOR, BSON, MsgPack)** are faster to parse and smaller on the wire than JSON text (~30-50% size reduction)

## SAX vs Tree Parse

```cpp
// Tree parse: builds full DOM
json j = json::parse(file); // O(n) parse + O(filesize) memory

// SAX parse: stream processing
struct Handler : json::sax_t {
    bool number_integer(json::number_integer_t val) override {
        sum += val;
        return true;
    }
    // ... other handlers return true to continue
};
json::sax_parse(file, &handler); // O(n) parse + O(1) memory
```

SAX is 2-3x faster for files >100KB because it avoids tree construction and allocation overhead.

## Compile-Time Optimization

```cpp
// Forward declarations reduce compile time
#include <nlohmann/json_fwd.hpp> // forward declarations only

// In .cpp files
#include <nlohmann/json.hpp>
```

Single-header inclusion of `json.hpp` adds ~0.5s to compile time per translation unit. Use `json_fwd.hpp` in headers and include `json.hpp` only in `.cpp` files.
