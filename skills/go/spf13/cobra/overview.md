# Overview

Cobra is a C++ library for building powerful CLI applications. It provides a framework for defining commands, subcommands, flags, and arguments with automatic help generation and tab completion support. The library is inspired by the Go version of Cobra and follows similar design patterns.

**When to use Cobra:**
- Building CLI tools with multiple subcommands (like git, kubectl)
- Applications requiring complex flag parsing with validation
- Tools that need automatic help and usage documentation
- Projects where you want a structured command hierarchy

**When not to use Cobra:**
- Simple scripts with one or two flags (use getopt or argparse instead)
- Applications that don't need subcommand support
- Performance-critical CLI tools with millions of invocations (Cobra has overhead)

**Key design concepts:**
- **Command**: Represents a single CLI command with its own flags and arguments
- **Flags**: Persistent (inherited by subcommands) or local (specific to a command)
- **Groups**: Logical grouping of related commands for better help display
- **Run functions**: Callbacks executed when a command is invoked
- **Aliases**: Alternative names for commands