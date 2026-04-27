# serde — Lifecycle

## Serialize

```rust
use serde::Serialize;

#[derive(Serialize)]
struct Config {
    url: String,
    timeout: u64,
}

let config = Config { url: "https://api.example.com".into(), timeout: 30 };
let json = serde_json::to_string(&config)?;
let pretty = serde_json::to_string_pretty(&config)?;
```

## Deserialize

```rust
use serde::Deserialize;

#[derive(Deserialize)]
struct Config {
    url: String,
    #[serde(default = "default_timeout")]
    timeout: u64,
}

fn default_timeout() -> u64 { 30 }

let config: Config = serde_json::from_str(r#"{"url": "https://api.example.com"}"#)?;
assert_eq!(config.timeout, 30); // default applied
```

## Derive vs Custom Implementation

**Derive (recommended for most cases):**
```rust
#[derive(Serialize, Deserialize)]
struct MyType { field: String }
```

**Custom implementation (when you need control):**
```rust
impl Serialize for MyType {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        // custom logic
    }
}
```

## Remote Derive (third-party types)

For types you don't own, use `#[serde(remote = "RemoteType")]`:

```rust
#[derive(Serialize, Deserialize)]
#[serde(remote = "chrono::DateTime<Utc>")]
struct DateTimeDef(chrono::DateTime<Utc>);

#[derive(Serialize, Deserialize)]
struct MyStruct {
    #[serde(with = "DateTimeDef")]
    timestamp: chrono::DateTime<Utc>,
}
```

## Attributes Reference

| Attribute | Effect |
|-----------|--------|
| `#[serde(rename = "...")]` | Rename field in serialized form |
| `#[serde(default)]` | Use `Default::default()` if field is missing |
| `#[serde(default = "fn")]` | Use function return value if field is missing |
| `#[serde(skip)]` | Skip field entirely |
| `#[serde(skip_serializing_if = "fn")]` | Skip if function returns true |
| `#[serde(deny_unknown_fields)]` | Error on unknown fields |
| `#[serde(borrow)]` | Borrow from input instead of allocating |
