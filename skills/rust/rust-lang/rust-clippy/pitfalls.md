# Pitfalls

```markdown
# Common Pitfalls with rust-lang/rust-clippy

## 1. Ignoring All Clippy Warnings

**BAD**: Suppressing all warnings without review
```rust
#![allow(clippy::all)]

fn main() {
    let x = 5;
    if x == 5 { return; } // Missing else branch
    println!("This never runs");
}
```

**GOOD**: Selectively allow specific lints
```rust
#![allow(clippy::needless_return)] // Intentional for readability

fn main() {
    let x = 5;
    if x == 5 {
        return;
    }
    println!("This never runs");
}
```

## 2. Over-relying on Automatic Fixes

**BAD**: Blindly applying all fixes
```bash
cargo clippy --fix --allow-dirty --allow-staged
```

**GOOD**: Review fixes before applying
```bash
# First, see what would change
cargo clippy --fix --dry-run

# Then apply with review
cargo clippy --fix
```

## 3. Using Wrong Lint Categories

**BAD**: Enabling pedantic lints in CI without review
```toml
[package.metadata.clippy]
"clippy::pedantic" = "deny"
```

**GOOD**: Start with default lints, then selectively enable
```toml
[package.metadata.clippy]
"clippy::pedantic" = "warn"
"clippy::nursery" = "allow"
"clippy::cargo" = "deny"
```

## 4. Not Configuring for Your Project

**BAD**: Using default configuration for all projects
```bash
cargo clippy
```

**GOOD**: Configure based on project needs
```toml
[package.metadata.clippy]
# For a library
"clippy::missing_docs_in_private_items" = "warn"
# For a binary
"clippy::print_stdout" = "deny"
```

## 5. Ignoring Performance Lints

**BAD**: Using inefficient patterns
```rust
fn process(data: &[u8]) {
    for i in 0..data.len() { // Use iter() instead
        println!("{}", data[i]);
    }
}
```

**GOOD**: Following Clippy's performance suggestions
```rust
fn process(data: &[u8]) {
    for item in data.iter() {
        println!("{}", item);
    }
}
```

## 6. Not Using `--fix` for Simple Issues

**BAD**: Manually fixing trivial issues
```rust
fn main() {
    let x = 5;
    return x; // Clippy suggests removing 'return'
}
```

**GOOD**: Let Clippy fix it automatically
```bash
cargo clippy --fix
```

## 7. Confusing Clippy with rustc Warnings

**BAD**: Treating all Clippy lints as errors
```bash
cargo clippy -- -D warnings
```

**GOOD**: Separate Clippy from compiler warnings
```bash
cargo clippy -- -W clippy::all -A warnings
```

## 8. Not Updating Clippy

**BAD**: Using outdated Clippy version
```bash
# Old version with known bugs
rustup component add clippy --toolchain 1.50.0
```

**GOOD**: Keep Clippy updated
```bash
rustup update
rustup component add clippy
```
```