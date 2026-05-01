# Overview

```markdown
# Overview of rust-lang/rust-clippy

## What is Clippy?

Clippy is the official Rust linter, providing over 600 lint checks to catch common mistakes, improve code quality, and enforce best practices. It's maintained by the Rust team and integrated directly with `cargo`.

## When to Use Clippy

**Use Clippy when:**
- You want to enforce code quality standards in your team
- You're learning Rust and want to avoid common pitfalls
- You're preparing code for production deployment
- You want to automatically fix common issues
- You need to maintain consistent code style across a large codebase

**Don't use Clippy when:**
- You're prototyping quickly and don't care about code quality
- You're working with legacy code that would require massive refactoring
- You need to suppress specific lints for performance-critical sections

## Key Design Principles

1. **Zero-cost abstractions**: Clippy lints are compile-time only, with no runtime overhead
2. **Configurable severity**: Each lint can be set to `allow`, `warn`, or `deny`
3. **Automatic fixes**: Many lints support `--fix` for automatic correction
4. **Extensible**: Custom lints can be created using the Clippy API

## Architecture

```
Source Code → Rust Compiler → AST Analysis → Clippy Lints → Warnings/Errors
```

Clippy operates as a compiler plugin, analyzing the Abstract Syntax Tree (AST) after parsing but before code generation.

## Integration Points

- **Cargo**: `cargo clippy` command
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins
- **IDE**: VS Code, IntelliJ, Vim with rust-analyzer
- **Build Systems**: Bazel, CMake (via cargo)

For more details on specific lints, see the [Clippy documentation](https://rust-lang.github.io/rust-clippy/).
```