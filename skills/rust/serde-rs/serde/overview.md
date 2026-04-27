# serde — Overview

**serde** is the standard Rust serialization/deserialization framework. It provides a trait-based architecture with derive macros (`#[derive(Serialize, Deserialize)]`) that generate parsing/generation code at compile time. It supports JSON, YAML, TOML, MessagePack, Bincode, and many other formats through data-format crates.

## When to Use

- Serializing/deserializing Rust structs to/from JSON, YAML, TOML, etc.
- Any API client/server that sends/receives structured data
- Configuration file parsing
- Data interchange between systems
- `no_std` environments (with `alloc`, `derive` feature)

## When NOT to Use

- Streaming parsers (serde requires full value in memory — use a streaming crate)
- Schema-less JSON with arbitrary keys (use `serde_json::Value`)
- Ultra-low-latency parsing where compile-time codegen overhead matters
- Self-referential or complex graph structures without `#[serde(borrow)]`

## Key Design

- **Traits**: `Serialize` (Rust → format) and `Deserialize` (format → Rust)
- **Derive macros**: `#[derive(Serialize, Deserialize)]` — zero-cost abstraction
- **Data model**: serde defines an intermediate data model; format crates map to/from it
- **Attributes**: `#[serde(rename = "foo")]`, `#[serde(default)]`, `#[serde(skip)]`, etc.
- **Zero-copy**: `#[serde(borrow)]` enables borrowing from the input buffer
