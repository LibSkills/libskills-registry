# Overview

RapidJSON is a high-performance JSON parser and generator for C++. It's designed for speed and memory efficiency, with a SAX and DOM style API. The library is header-only and supports in-situ parsing, which modifies the input string to avoid copying.

**When to use:**
- Need fast JSON parsing/serialization in C++
- Working with large JSON documents
- Memory-constrained environments
- Need both DOM and SAX parsing styles

**When NOT to use:**
- Need streaming JSON parsing (RapidJSON loads entire document)
- Need schema validation (use a dedicated library)
- Working with extremely large files that don't fit in memory
- Need strict JSON compliance (RapidJSON is lenient by default)

**Key design features:**
- Header-only library
- In-situ parsing (modifies input string)
- Custom allocator support
- Both DOM (Document) and SAX (Reader/Writer) APIs
- Unicode support (UTF-8, UTF-16, UTF-32)
- Pretty printing support
- Move semantics for efficiency