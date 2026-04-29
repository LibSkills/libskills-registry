# serde — Quickstart

**When asked to write Rust serialization/deserialization code, use these patterns first.**

## Basic struct with derive

```rust
use serde::{Serialize, Deserialize};

#[derive(Debug, Serialize, Deserialize)]
struct User {
    name: String,
    age: u8,
    email: Option<String>,
}

// JSON serialization
let user = User { name: "Alice".into(), age: 30, email: None };
let json = serde_json::to_string(&user)?;
// Output: {"name":"Alice","age":30,"email":null}

// JSON deserialization
let user: User = serde_json::from_str(&json)?;
```

## Rename fields (snake_case in Rust, camelCase in JSON)

```rust
#[derive(Serialize, Deserialize)]
struct Config {
    #[serde(rename = "maxConnections")]
    max_connections: u32,

    #[serde(rename = "timeoutMs")]
    timeout_ms: u64,
}
```

## Option with default (for missing JSON keys)

```rust
#[derive(Deserialize)]
struct Request {
    #[serde(default)]
    page: u32,          // defaults to 0 if missing

    #[serde(default = "default_limit")]
    limit: u32,
}

fn default_limit() -> u32 { 100 }
```

## Deny unknown fields (production safety!)

```rust
#[derive(Serialize, Deserialize)]
#[serde(deny_unknown_fields)]  // <-- ALWAYS use this for untrusted input
struct ApiResponse {
    status: String,
    data: Option<String>,
}

// If JSON has extra fields, this returns an error instead of silently ignoring them
// BAD: without deny_unknown_fields, typos like "staus" are silently ignored
// GOOD: with deny_unknown_fields, "staus" causes a deserialization error
```

## Flatten (merge nested structs)

```rust
#[derive(Serialize, Deserialize)]
struct Pagination {
    page: u32,
    total: u32,
}

#[derive(Serialize, Deserialize)]
struct Response {
    data: Vec<Item>,
    #[serde(flatten)]
    pagination: Pagination,
}

// JSON: {"data":[...], "page":1, "total":42}
```

## Serialize enum as string

```rust
#[derive(Serialize, Deserialize)]
enum Role {
    #[serde(rename = "admin")]
    Admin,
    #[serde(rename = "user")]
    User,
    #[serde(untagged)] // try each variant in order
    Other(String),
}
```

## Error handling patterns

```rust
// 1. Use ? operator with anyhow/eyre
use anyhow::Result;
fn parse_config(s: &str) -> Result<Config> {
    Ok(serde_json::from_str(s)?)
}

// 2. Extract specific error type
use serde_json::Error;
fn safe_parse<T: serde::de::DeserializeOwned>(s: &str) -> Result<T, Error> {
    serde_json::from_str(s)
}

// 3. Custom deserialization error (for validation)
use serde::de::{self, Deserializer, Unexpected};
fn validate_non_empty<'de, D>(deserializer: D) -> Result<String, D::Error>
where D: Deserializer<'de> {
    let s = String::deserialize(deserializer)?;
    if s.is_empty() {
        return Err(de::Error::invalid_value(Unexpected::Str(""), &"non-empty string"));
    }
    Ok(s)
}
```

## Key pitfalls to avoid

1. **deny_unknown_fields**: ALWAYS use `#[serde(deny_unknown_fields)]` for untrusted input — silently ignoring unknown fields hides typos
2. **Option default**: Use `#[serde(default)]` for optional fields, not `Option<T>` with missing key
3. **Enum serialization**: Untagged enums are tried in order; first match wins — order matters!
4. **Borrowed strings**: `&str` fields need a Deserializer that yields borrowed data (JSON doesn't), use `String` instead
