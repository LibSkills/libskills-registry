# serde — Best Practices

## Prefer externally tagged or internally tagged enums

Untagged enums are fragile. Use explicit tags for unambiguous deserialization.

```rust
// Recommended: internally tagged
#[derive(Serialize, Deserialize)]
#[serde(tag = "type")]
enum Event {
    Click { x: i32, y: i32 },
    KeyPress { key: char },
}
// JSON: {"type": "Click", "x": 10, "y": 20}
```

## Use `#[serde(default)]` for forward compatibility

Adding new fields should not break existing serialized data.

```rust
#[derive(Deserialize)]
struct Config {
    url: String,
    #[serde(default)]
    timeout: Option<u64>,     // None if missing
    #[serde(default = "default_retries")]
    retries: u32,              // 3 if missing
}
fn default_retries() -> u32 { 3 }
```

## Use `#[serde(rename_all = "camelCase")]` for JSON APIs

Most JSON APIs use camelCase. Serde supports automatic renaming conventions:

```rust
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct ApiResponse {
    user_id: u64,      // serialized as "userId"
    first_name: String, // serialized as "firstName"
    created_at: String, // serialized as "createdAt"
}
```

Available conventions: `lowercase`, `UPPERCASE`, `PascalCase`, `camelCase`, `snake_case`, `SCREAMING_SNAKE_CASE`, `kebab-case`, `SCREAMING-KEBAB-CASE`

## Use `#[serde(skip_serializing_if)]` for optional fields

Skip serializing `None` or default values to produce cleaner output.

```rust
#[derive(Serialize)]
struct Request {
    query: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    page: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    limit: Option<u32>,
}
// Output: {"query": "search term"}  (no null fields)
```

## Use `#[serde(transparent)]` for newtype wrappers

Serializes/deserializes the inner value directly, without a wrapping layer.

```rust
#[derive(Serialize, Deserialize)]
#[serde(transparent)]
struct UserId(u64);
// JSON: 42 (not {"UserId": 42})
```

## Validate after deserialization

Serde validates types, not semantics. Add a `validate()` method for domain constraints.

```rust
impl Config {
    fn validate(&self) -> Result<(), &'static str> {
        if self.timeout == 0 { return Err("timeout must be non-zero"); }
        if self.retries > 10 { return Err("max 10 retries"); }
        Ok(())
    }
}
```
