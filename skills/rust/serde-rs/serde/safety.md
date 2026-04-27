# serde — Safety

Red lines — conditions that must NEVER occur.

## NEVER deserialize `#[serde(untagged)]` enums from untrusted input without validation

Untagged enums try all variants in order. An attacker can craft input that matches an unintended variant, potentially bypassing validation or triggering unsafe code paths. Always validate the deserialized variant explicitly.

```rust
// BAD: attacker-controlled variant selection
#[derive(Deserialize)]
#[serde(untagged)]
enum Command { Admin { ... }, User { ... } }
// Input: {"role": "admin"} → may parse as User variant if User lists "role" field first

// GOOD: externally tagged with explicit match
#[derive(Deserialize)]
#[serde(tag = "type")]
enum Command { Admin { ... }, User { ... } }
let cmd: Command = serde_json::from_str(input)?;
match cmd { Command::Admin { .. } => { /* authenticated separately */ }, _ => Err(...) }
```

## NEVER use `deserialize_any` with untrusted input

`serde_json::Value` and similar `deserialize_any` implementations accept arbitrary JSON. This includes deeply nested structures that can cause stack overflow on deserialization. Set a recursion limit when parsing untrusted data.

```rust
// For untrusted input, use serde_json::from_reader with depth limiting
// or set serde_json::Deserializer::from_str(input).disable_recursion_limit()
```

## NEVER skip validation on deserialized data that crosses trust boundaries

Serde guarantees that the data matches the Rust type, but it does not guarantee semantic validity. A `u8` field will parse as `u8`, but it may represent an invalid state for your domain. Always validate after deserialization.

```rust
// BAD: trusting parsed data
#[derive(Deserialize)]
struct Config { port: u16 }
let cfg: Config = serde_json::from_str(input)?;
std::net::TcpListener::bind(("0.0.0.0", cfg.port))?; // port 0 is valid u16 but invalid bind

// GOOD: validate semantics
if cfg.port == 0 { return Err("port must be non-zero".into()); }
```

## NEVER use `#[serde(borrow)]` with long-lived types from short-lived input

Borrowed deserialization creates references into the input buffer. If the deserialized type outlives the buffer, it contains dangling references. This is a memory safety violation in safe Rust (lifetime errors become confusing compile errors — but with `unsafe` or `transmute`, it becomes UB).
