# serde — Pitfalls

## Do NOT use untagged enums for deserialization with overlapping fields

`#[serde(untagged)]` tries variants in order and picks the first successful parse. If variants share field names, the wrong variant may be silently chosen.

```rust
// BAD: ambiguous — both variants have "type" field
#[derive(Deserialize)]
#[serde(untagged)]
enum Message {
    Text { type: String, content: String },
    Image { type: String, url: String },
}
// Input: {"type": "image", "url": "photo.png"} → may parse as Text variant!

// GOOD: use externally tagged or internally tagged
#[derive(Deserialize)]
#[serde(tag = "type")]
enum Message {
    Text { content: String },
    Image { url: String },
}
```

## `deny_unknown_fields` — know when to use it

`#[serde(deny_unknown_fields)]` rejects JSON with unknown keys. This is **good for security** but **bad for forward compatibility**.

```rust
// This breaks when API adds new fields:
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Config { url: String }
// Input: {"url": "...", "timeout": 30} → Error!
```

**Choose based on your scenario:**

| Scenario | Recommended |
|---|----|
| External API / user input — catch typos and injection | ✅ Use `deny_unknown_fields` |
| Evolving API — new fields may appear | ❌ Skip it, or use `#[serde(default)]` on optional fields |
| Both strict + compatible — validation first, lenient fallback | Write a custom `Deserialize` that validates, then falls back |
| Internal config file you control | Usually unnecessary; use it if you want to catch renames |

A practical middle-ground pattern:

```rust
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct StrictConfig {
    url: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    timeout: Option<u64>,  // optional now, might become required later
}
// Input: {"url": "...", "timeout": 30} → OK
// Input: {"url": "...", "unknown": "x"} → Error (catches typos)
```

## Do NOT use `#[serde(flatten)]` with duplicate keys

`#[serde(flatten)]` merges nested struct fields into the parent. If the flattened struct has fields with the same name as the parent or another flattened struct, behavior is undefined — serde may pick either value or panic.

```rust
// BAD: both structs have "name" — undefined behavior
#[derive(Deserialize)]
struct Outer {
    name: String,
    #[serde(flatten)]
    inner: Inner,
}
#[derive(Deserialize)]
struct Inner { name: String, value: i32 }
```

## Do NOT use borrowed deserialization without understanding lifetime constraints

`#[serde(borrow)]` borrows string data from the input buffer. The deserialized struct must not outlive the input.

```rust
// BAD: return value outlives input
fn parse<'a>(input: &'a str) -> MyStruct<'a> {
    serde_json::from_str(input).unwrap()
}
// Now MyStruct borrows from 'input, tying its lifetime to it
// Might be what you want, but often surprising
```

## Do NOT nest recursive types without Box

Serde generates code that needs to know the size of the type at compile time. A recursive type without indirection causes infinite-size compilation errors.

```rust
// BAD: infinite size
#[derive(Serialize, Deserialize)]
struct Node { children: Vec<Node> }

// GOOD: Box breaks recursion
#[derive(Serialize, Deserialize)]
struct Node { children: Vec<Box<Node>> }
```

## Do NOT rely on field ordering for untagged or internally tagged enums

Serde does not guarantee that internally-tagged or adjacently-tagged enum fields are processed in struct declaration order. If ordering matters, use externally-tagged representation.
