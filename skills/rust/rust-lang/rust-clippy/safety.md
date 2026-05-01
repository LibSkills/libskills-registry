# Safety

```markdown
# Safety Considerations with rust-lang/rust-clippy

## 1. NEVER Disable All Safety Lints

**BAD**: Allowing all unsafe-related lints
```rust
#![allow(clippy::all)]
#![allow(unsafe_code)]

unsafe fn dangerous() {
    // No safety checks
    let ptr = std::ptr::null_mut();
    *ptr = 42; // Undefined behavior!
}
```

**GOOD**: Keep safety lints enabled
```rust
#![deny(unsafe_code)]

fn safe_function() {
    // Safe code only
    let mut x = 42;
    println!("{}", x);
}
```

## 2. NEVER Ignore `clippy::cast_lossless`

**BAD**: Ignoring potential data loss
```rust
fn main() {
    let large: u64 = 1_000_000_000_000;
    let small: u32 = large as u32; // Data loss!
    println!("{}", small);
}
```

**GOOD**: Handle potential overflow
```rust
fn main() {
    let large: u64 = 1_000_000_000_000;
    let small: u32 = large.try_into().expect("Value too large");
    println!("{}", small);
}
```

## 3. NEVER Use `unwrap()` Without Clippy Checking

**BAD**: Unchecked unwrap
```rust
fn main() {
    let result: Result<i32, String> = Err("error".to_string());
    let value = result.unwrap(); // Panics!
    println!("{}", value);
}
```

**GOOD**: Handle errors properly
```rust
fn main() -> Result<(), String> {
    let result: Result<i32, String> = Err("error".to_string());
    let value = result?;
    println!("{}", value);
    Ok(())
}
```

## 4. NEVER Ignore `clippy::panic`

**BAD**: Using panic in library code
```rust
pub fn divide(a: i32, b: i32) -> i32 {
    if b == 0 {
        panic!("Division by zero!"); // Library should not panic
    }
    a / b
}
```

**GOOD**: Return Result instead
```rust
pub fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        return Err("Division by zero".to_string());
    }
    Ok(a / b)
}
```

## 5. NEVER Use `unsafe` Without Clippy's `unsafe_derive_deserialize`

**BAD**: Unsafe code without validation
```rust
#![allow(clippy::unsafe_derive_deserialize)]

#[derive(Deserialize)]
struct UnsafeStruct {
    ptr: *mut i32, // Unsafe to deserialize
}
```

**GOOD**: Validate unsafe deserialization
```rust
#[derive(Deserialize)]
struct SafeStruct {
    index: usize,
}

impl SafeStruct {
    fn get_ptr(&self, buffer: &[i32]) -> Option<&i32> {
        buffer.get(self.index)
    }
}
```

## Red Line Conditions Summary

| Condition | Severity | Action |
|-----------|----------|--------|
| Disabling all safety lints | Critical | Never allow |
| Ignoring cast_lossless | High | Always fix |
| Unchecked unwrap() | High | Use proper error handling |
| panic() in library code | High | Return Result |
| Unsafe deserialization | Critical | Validate all inputs |
```