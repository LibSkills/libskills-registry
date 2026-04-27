# fmt — Overview

**{fmt}** is a modern C++ formatting library that provides a fast, safe alternative to `printf` and `iostreams`. It's the implementation basis for C++20 `std::format` and is used as the formatting backend in spdlog. Supports compile-time format string checking, user-defined type formatting, and color output.

## When to Use

- Any C++ application that formats strings (replaces `printf`, `sprintf`, `std::stringstream`)
- Logging backends (spdlog uses fmt internally)
- User-facing text output with localization support
- Compile-time format string validation (catches type errors at build time)
- High-performance formatting in hot paths

## When NOT to Use

- C code without C++11 (use `printf`)
- When `std::format` (C++20) is sufficient and you want zero-dependency
- Localization-heavy apps requiring ICU (fmt supports locales but isn't a full i18n solution)
- Ultra-minimal embedded systems (header + compiled library adds ~100KB)

## Key Design

- **Format syntax**: `"{}"` for positional, `"{0}"` for indexed, `"{name}"` for named args
- **Compile-time checks**: `FMT_STRING()` or C++20 `fmt::format()` validates types at compile time
- **Extensible**: specialize `fmt::formatter<T>` for custom types
- **Fast**: typically 2-5x faster than `printf`, 10-30x faster than `iostreams`
- **Safe**: type mismatch is a compile error (with compile-time checking) or exception (at runtime)
