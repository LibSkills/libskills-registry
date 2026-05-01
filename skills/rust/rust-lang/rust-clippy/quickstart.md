# Quickstart

```markdown
# Quickstart Guide for rust-lang/rust-clippy

## Installation

Add Clippy to your Rust project:

```bash
# Install via rustup (recommended)
rustup component add clippy

# Or add as a Cargo dependency
cargo add clippy
```

## Basic Usage

### 1. Run Clippy on your project

```bash
# Run all lints
cargo clippy

# Run with specific lint levels
cargo clippy -- -W clippy::pedantic -A clippy::style
```

### 2. Fix warnings automatically

```bash
# Apply automatic fixes
cargo clippy --fix

# Fix with backup
cargo clippy --fix --allow-dirty
```

### 3. Suppress specific lints

```rust
// Suppress a lint for the entire file
#![allow(clippy::needless_return)]

// Suppress for a specific function
#[allow(clippy::too_many_arguments)]
fn complex_function(a: i32, b: i32, c: i32, d: i32, e: i32, f: i32) {
    // ...
}

// Suppress for a single line
#[allow(clippy::cast_lossless)]
let x = y as u32;
```

### 4. Configure lint levels in Cargo.toml

```toml
[package.metadata.clippy]
# Set lint levels
"clippy::pedantic" = "warn"
"clippy::nursery" = "allow"
"clippy::cargo" = "deny"
```

### 5. Use with CI/CD

```yaml
# GitHub Actions example
- name: Run Clippy
  run: cargo clippy -- -D warnings
```

### 6. Generate lint report

```bash
# Generate JSON output for tooling
cargo clippy --message-format=json > clippy_report.json
```

## Common Lint Categories

| Category | Description | Example Lints |
|----------|-------------|---------------|
| `clippy::style` | Code style issues | `needless_return`, `single_match` |
| `clippy::complexity` | Overly complex code | `cognitive_complexity`, `cyclomatic_complexity` |
| `clippy::perf` | Performance issues | `large_enum_variant`, `unnecessary_cast` |
| `clippy::pedantic` | Strict correctness | `cast_lossless`, `missing_docs_in_private_items` |
| `clippy::nursery` | Experimental lints | `use_self`, `match_same_arms` |
```