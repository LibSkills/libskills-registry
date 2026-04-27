# serde — Performance

Serde's performance depends heavily on the data format crate and the serialization strategy.

## Format Performance (relative)

| Format | Speed | Size | Notes |
|--------|-------|------|-------|
| `bincode` | Fastest | Compact | Binary, no self-describing |
| `postcard` | Very fast | Very compact | `no_std`, COBS framing |
| `rmp-serde` (MessagePack) | Fast | Compact | Binary, self-describing |
| `serde_json` | Moderate | Verbose | Human-readable |
| `toml` | Slow | Verbose | Configuration format |

## Optimization Techniques

**Prefer borrowed deserialization for zero-copy:**
```rust
#[derive(Deserialize)]
struct Data<'a> {
    #[serde(borrow)]
    items: Vec<&'a str>,  // borrowed from input buffer
}
```

**Avoid allocating for optional fields:**
```rust
// Prefer Option<&str> over Option<String> when borrowing
#[derive(Deserialize)]
struct Config<'a> {
    name: &'a str,
    description: Option<&'a str>,
}
```

**Use `BufReader` for file/network deserialization:**
```rust
use std::io::BufReader;
let file = std::fs::File::open("large.json")?;
let reader = BufReader::new(file);
let data: Vec<Item> = serde_json::from_reader(reader)?;
```

## JSON-Specific Performance

- `serde_json::to_writer` is faster than `serde_json::to_string` (no intermediate string)
- `serde_json::from_reader` is faster than `serde_json::from_str` (no full buffer in memory)
- Use `serde_json::from_slice` instead of `serde_json::from_str` to avoid UTF-8 validation on known-valid input
- The `arbitrary_precision` feature slows down number parsing significantly — only enable if you need it

## Compile-Time Cost

- Derive macros generate code at compile time — this is zero-cost at runtime but increases build time for large projects
- Many formats support `no_std` with `alloc` (no heap allocations beyond what the type requires)
