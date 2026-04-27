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

## Do NOT use `deny_unknown_fields` in APIs that may evolve

`#[serde(deny_unknown_fields)]` rejects JSON with unknown keys. This breaks forward compatibility — a newer API version adding a field will cause your deserialization to fail.

```rust
// BAD: breaks when API adds new fields
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Config { url: String }
// Input: {"url": "...", "timeout": 30} → Error!

// GOOD: silently ignore unknown fields (default behavior)
#[derive(Deserialize)]
struct Config { url: String }
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
