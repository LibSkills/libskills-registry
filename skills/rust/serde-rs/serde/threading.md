# serde — Threading

**Serde is purely a data transformation layer. It has no internal threading model, no shared state, and no synchronization primitives.**

- `Serialize` and `Deserialize` trait implementations are stateless by default
- Parallel serialization/deserialization is safe as long as each thread processes independent data
- Serde itself performs no I/O — threading behavior depends entirely on the data format crate (e.g., `serde_json`, `toml`)

## Thread-Safe by Default

All serde derive-generated code is thread-safe. There is no shared mutable state. You can serialize/deserialize from multiple threads concurrently without any synchronization.

```rust
use std::thread;

let data = MyStruct { field: "hello".into() };
let json = serde_json::to_string(&data).unwrap();

// Safe: each thread processes its own copy
thread::scope(|s| {
    s.spawn(|| {
        let _: MyStruct = serde_json::from_str(&json).unwrap();
    });
    s.spawn(|| {
        let _: MyStruct = serde_json::from_str(&json).unwrap();
    });
});
```

## Caution: Manual Trait Implementations

If you write custom `Serialize` or `Deserialize` implementations that use shared mutable state (e.g., caching, counters), you are responsible for synchronization. Derive-generated implementations never do this.
