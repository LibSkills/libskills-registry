# Overview

Nana is a cross-platform C++ GUI library designed to provide a modern, standard-like interface for creating graphical user interfaces. It supports Windows (via native Win32 API), Linux (via X11), and experimental support for macOS and FreeBSD. The library emphasizes a clean, C++17-compatible API that feels familiar to developers coming from the C++ standard library.

**When to use Nana:**
- You need a lightweight, header-only-style GUI library for C++ projects
- You want cross-platform GUI without heavy dependencies like Qt or wxWidgets
- You prefer a modern C++ style with RAII, lambdas, and type-safe event handling
- You need basic to intermediate GUI features: forms, buttons, textboxes, layouts, timers, drawing

**When NOT to use Nana:**
- You need advanced widgets like tree views, rich text editors, or complex data grids
- You require native look-and-feel on all platforms (Nana uses its own rendering)
- You need accessibility features or screen reader support
- You're targeting embedded systems or mobile platforms (no mobile support)
- You need high-performance 3D graphics or GPU acceleration

**Key design principles:**
- **Widget hierarchy**: All widgets are children of a parent window (usually `nana::form`)
- **Event system**: Uses `events()` member function returning an event handler object with lambdas
- **Layout management**: `nana::place` provides a flexible div-based layout system similar to CSS
- **Graphics**: `nana::paint::graphics` for custom drawing, `nana::drawing` for event-driven rendering
- **Thread safety**: UI operations must be performed on the main thread; use `nana::internal_scope_guard` for thread-safe access

The library is licensed under the Boost Software License, making it suitable for both open-source and commercial projects.