# Performance

```markdown
# Performance Characteristics of rust-lang/rust-clippy

## Compilation Time Impact

### Baseline Performance

```bash
# Without Clippy
time cargo build
# ~10 seconds

# With Clippy
time cargo clippy
# ~12 seconds (20% overhead)
```

### Optimization Tips

```bash
# Use incremental compilation
CARGO_INCREMENTAL=1 cargo clippy

# Only check changed files
cargo clippy --workspace --all-targets
```

## Memory Usage Patterns

### Lint Analysis Memory

```rust
// BAD: Large allocations in hot paths
fn process_large_data(data: &[u8]) {
    let mut buffer = Vec::with_capacity(data.len());
    for &byte in data {
        buffer.push(byte);
    }
    // Clippy warns about unnecessary allocation
}

// GOOD: Use slices directly
fn process_large_data(data: &[u8]) {
    for &byte in data {
        // Process directly
    }
}
```

## Allocation Patterns

### Avoiding Unnecessary Allocations

```rust
// BAD: Multiple allocations
fn build_string(items: &[&str]) -> String {
    let mut result = String::new();
    for item in items {
        result.push_str(item);
        result.push_str(", ");
    }
    result
}

// GOOD: Pre-allocate capacity
fn build_string(items: &[&str]) -> String {
    let total_len: usize = items.iter().map(|s| s.len() + 2).sum();
    let mut result = String::with_capacity(total_len);
    for item in items {
        result.push_str(item);
        result.push_str(", ");
    }
    result
}
```

## Cache-Friendly Patterns

```rust
// BAD: Non-contiguous memory access
fn process_matrix(matrix: &Vec<Vec<i32>>) {
    for col in 0..matrix[0].len() {
        for row in 0..matrix.len() {
            println!("{}", matrix[row][col]); // Cache miss!
        }
    }
}

// GOOD: Contiguous memory access
fn process_matrix(matrix: &Vec<Vec<i32>>) {
    for row in matrix {
        for &value in row {
            println!("{}", value); // Cache friendly
        }
    }
}
```

## Lint Performance Categories

| Category | Performance Impact | Typical Overhead |
|----------|-------------------|------------------|
| `clippy::style` | Low | <5% |
| `clippy::complexity` | Medium | 10-20% |
| `clippy::perf` | Low | <5% |
| `clippy::pedantic` | High | 20-40% |
| `clippy::nursery` | Variable | 10-50% |

## Optimization Strategies

### 1. Selective Lint Enabling

```toml
# Only enable performance-critical lints
[package.metadata.clippy]
"clippy::perf" = "deny"
"clippy::style" = "allow"
```

### 2. Use `--fix` for Performance Improvements

```bash
# Automatically apply performance fixes
cargo clippy --fix -- -W clippy::perf
```

### 3. Profile Before Optimizing

```bash
# Profile compilation time
cargo clippy --timings

# Profile runtime performance
cargo clippy --release
```

## Benchmarking Clippy Impact

```rust
#[bench]
fn bench_with_clippy(b: &mut Bencher) {
    b.iter(|| {
        // Code that Clippy might optimize
        let mut vec = Vec::new();
        for i in 0..1000 {
            vec.push(i);
        }
        vec
    });
}
```
```