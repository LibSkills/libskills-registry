# Best Practices

```markdown
# Best Practices for rust-lang/rust-clippy

## 1. Gradual Adoption Strategy

Start with default lints and progressively enable more:

```toml
# Phase 1: Default lints
[package.metadata.clippy]

# Phase 2: Add style lints
"clippy::style" = "warn"

# Phase 3: Add pedantic lints (with exceptions)
"clippy::pedantic" = "warn"
"clippy::missing_docs_in_private_items" = "allow"
```

## 2. Use Configuration Files

Create `.clippy.toml` for project-wide settings:

```toml
# .clippy.toml
cognitive-complexity-threshold = 15
cyclomatic-complexity-threshold = 25
too-many-arguments-threshold = 7
too-many-lines-threshold = 200
```

## 3. Integrate with CI Pipeline

```yaml
# .github/workflows/clippy.yml
name: Clippy Check
on: [push, pull_request]
jobs:
  clippy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
          components: clippy
      - uses: actions-rs/clippy-check@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          args: -- -D warnings
```

## 4. Use Lint Groups Effectively

```rust
// In lib.rs or main.rs
#![deny(clippy::all)]
#![warn(clippy::pedantic)]
#![allow(clippy::missing_docs_in_private_items)]
#![allow(clippy::module_name_repetitions)]
```

## 5. Create Custom Lint Rules

```rust
// custom_lint.rs
use clippy_utils::diagnostics::span_lint_and_help;
use rustc_lint::{LateContext, LateLintPass};
use rustc_span::sym;

declare_clippy_lint! {
    pub const MY_CUSTOM_LINT: rustc_lint::Lint = "my_custom_lint";
    "description of my custom lint"
}
```

## 6. Document Lint Suppressions

```rust
/// # Safety
/// This function intentionally uses `unwrap()` because the input
/// is guaranteed to be valid by the caller.
#[allow(clippy::unwrap_used)]
fn process_valid_input(data: &str) -> i32 {
    data.parse().unwrap()
}
```

## 7. Regular Maintenance

```bash
# Update Clippy regularly
rustup update

# Run Clippy on all targets
cargo clippy --all-targets -- -D warnings

# Check for new lints
cargo clippy -- -W clippy::nursery
```

## 8. Team Workflow

1. **Code Review**: Include Clippy output in PR reviews
2. **Pre-commit Hooks**: Run Clippy before commits
3. **Documentation**: Maintain a list of allowed lints with reasons
4. **Training**: Teach team members about common Clippy suggestions
```