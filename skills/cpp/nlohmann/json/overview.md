# nlohmann/json — Overview

**nlohmann/json** (Niels Lohmann's JSON library) is a header-only C++ library for JSON parsing, serialization, and manipulation. It provides an intuitive API that mirrors Python's `json` module and JavaScript's object literals.

## When to Use

- C++ applications that need JSON parsing or generation (REST clients, config files, serialization)
- Any project where JSON is the interchange format and you want minimal boilerplate
- Prototyping and tools where developer ergonomics matter more than maximum throughput
- Header-only convenience (just `#include <nlohmann/json.hpp>` — no build system changes needed)

## When NOT to Use

- Ultra-high-throughput JSON processing (>100MB/s) — consider simdjson, RapidJSON, or sajson
- Real-time or latency-critical paths where allocations are not acceptable (nlohmann/json allocates freely)
- Embedded systems with tight memory constraints (binary size and heap usage are significant)
- When you only need partial parsing / streaming (SAX is inconvenient; use simdjson's on-demand API)

## Key Design

- **Header-only**: `#include <nlohmann/json.hpp>` — `json` type is `nlohmann::json` (alias `nlohmann::ordered_json` for ordered keys)
- **Type deduction**: parse to `json`, read with `get<T>()` or `as<T>()`, assign with `operator=`
- **Exception-based errors**: parsing failure, type mismatch, out-of-range all throw `json::exception`
- **SAX interface**: `json::sax_parse()` for streaming/event-driven parsing without building the whole tree
- **Custom serialization**: `nlohmann::adl_serializer<T>` specialization for user types
