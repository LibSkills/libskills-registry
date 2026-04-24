# LibSkills Specification v1

This document defines the LibSkills Protocol — the standard for packaging, distributing, and consuming library operational knowledge.

---

## 1. Core Concept

LibSkills is a **Knowledge Package Manager**. Each "skill" is a collection of structured, chunked knowledge files about a specific open-source library. The goal is to give AI agents everything they need to use a library correctly — without guessing, without reading the full source, and without hallucinating.

## 2. Registry Structure

### 2.1 Repository Layout

```
registry/
├── index.json                    # Master index of all skills
├── cpp/
│   ├── gabime/
│   │   └── spdlog/
│   │       ├── skill.json        # Metadata only
│   │       ├── tier1/            # Official, curated knowledge
│   │       │   ├── overview.md
│   │       │   ├── api.md
│   │       │   ├── pitfalls.md
│   │       │   ├── threading.md
│   │       │   ├── lifecycle.md
│   │       │   ├── memory.md
│   │       │   ├── safety.md
│   │       │   ├── performance.md
│   │       │   └── examples/
│   │       │       └── basic.cpp
│   │       └── tier2/            # Community-submitted knowledge
│   │           ├── community-a/
│   │           └── community-b/
│   └── nlohmann/
│       └── json/
│           └── ...               # Same structure
├── rust/
│   └── tokio-rs/
│       └── tokio/
│           └── ...
├── python/
│   └── psf/
│       └── requests/
│           └── ...
├── go/
└── js/
```

### 2.2 Naming Convention

```
registry/{language}/{author}/{name}/
```

- `language`: `cpp`, `rust`, `python`, `go`, `js`
- `author`: GitHub username or organization
- `name`: library name

### 2.3 Tier Structure

Each skill has two tiers:

- **tier1/**: Official, reviewed, high-confidence knowledge. Maintained by LibSkills team or trusted maintainers.
- **tier2/**: Community-submitted knowledge. Open to everyone. May include multiple community variants.

AI agents should prefer `tier1/` over `tier2/` when both exist.

### 2.4 Group Classification

- **Main**: De-facto standard libraries (spdlog, fmt, tokio, serde, requests, numpy, react, express)
- **Contrib**: Niche, smaller, or newer libraries

## 3. Skill Metadata (`skill.json`)

### 3.1 Schema

```jsonc
{
  "name": "spdlog",
  "repo": "gabime/spdlog",
  "language": "cpp",
  "tier": "tier1",
  "group": "main",
  "version": "1.14.2",
  "skill_version": "1.0.0",
  "schema": "libskills/v1",

  "trust_score": 95,
  "verified": true,
  "official": true,
  "updated_at": "2026-04-25T00:00:00Z",

  "trust_score_sources": {
    "official_review": 40,
    "stars": 20,
    "community_votes": 20,
    "update_freshness": 15,
    "issue_health": 5
  },

  "completeness": 85,

  "tags": [
    "logging",
    "async",
    "thread-safe",
    "header-only"
  ],

  "compatibility": {
    "c++": ["17", "20", "23"],
    "platforms": ["linux", "macos", "windows"]
  },

  "dependencies": {
    "required": ["fmt"],
    "optional": []
  },

  "files": {
    "tier1": [
      "overview.md",
      "api.md",
      "pitfalls.md",
      "threading.md",
      "lifecycle.md",
      "memory.md",
      "safety.md",
      "performance.md",
      "examples/basic.cpp"
    ],
    "tier2": []
  }
}
```

### 3.2 Required Fields

| Field | Description |
|-------|-------------|
| `name` | Library name |
| `repo` | GitHub repo (author/name) |
| `language` | Primary language |
| `tier` | `tier1` or `tier2` |
| `group` | `main` or `contrib` |
| `version` | Library version this skill targets |
| `skill_version` | Version of this skill file |
| `schema` | `libskills/v1` |
| `trust_score` | 0–100 |
| `updated_at` | ISO 8601 timestamp |
| `tags` | Array of tags for search |
| `files` | List of files included |

### 3.3 Trust Score Calculation

| Component | Max Score | Source |
|-----------|-----------|--------|
| Official Review | 40 | Tier 1 maintainer review |
| Stars | 20 | Based on GitHub stars tier |
| Community Votes | 20 | User ratings and usage |
| Update Freshness | 15 | Skill updated within 60 days of library release |
| Issue Health | 5 | Low open issue count relative to stars |

## 4. Knowledge Files

Each file should be **500–1500 tokens** (not characters). This keeps each chunk small enough for an AI agent to consume efficiently.

### 4.1 `overview.md`

Brief description of the library, its purpose, and when to use it.

### 4.2 `api.md`

Core API usage patterns. Include minimal working code snippets. Focus on the 20% of APIs that cover 80% of use cases.

### 4.3 `pitfalls.md`

**The most important file.** Common mistakes and anti-patterns. What NOT to do. This is where most hallucination errors are prevented.

```markdown
## Anti-Patterns

### Do NOT use std::endl
`spdlog` is binary-safe. Using `std::endl` flushes the buffer on every write.
Always use `\n` or let the logger handle flushing.

### Do NOT pass temporary strings for format args
```cpp
// BAD
spdlog::info("Value: {}", std::to_string(x));  // Heap allocation
// GOOD
spdlog::info("Value: {}", x);  // spdlog handles formatting
```

### Do NOT use default logger in static destructors
The default logger may already be destroyed. See `lifecycle.md`.
```

### 4.4 `threading.md`

Thread safety guarantees, async behavior, and concurrency constraints.

```markdown
## Thread Safety

- Default logger: NOT thread-safe by default
- `spdlog::async_logger`: thread-safe, uses background thread pool
- `sinks`: depends on sink type (basic_file_sink is NOT thread-safe)

## Async Mode

spdlog::init_thread_pool(queue_size=8192, threads=1);
auto logger = spdlog::create_async<spdlog::sinks::basic_file_sink_mt>("async", "logs/app.log");
```

### 4.5 `lifecycle.md`

Initialization, shutdown, and ordering constraints.

```markdown
## Initialization

Call `spdlog::set_default_logger()` before any logging in static initializers.

## Shutdown

Always call `spdlog::shutdown()` before process exit to flush all loggers.
Never call `shutdown()` inside a static destructor — use `atexit()`.
```

### 4.6 `memory.md`

Resource management, ownership, and leak patterns.

### 4.7 `safety.md`

Red lines — conditions that must NEVER occur. If an AI agent detects these patterns in its output, it should stop and warn.

```markdown
## Red Lines

- NEVER use logger after fork() without recreating it
- NEVER destroy logger before flush
- NEVER share `basic_file_sink` across threads without synchronization
- NEVER use `%s` format strings — always use {} formatting
```

### 4.8 `performance.md`

Throughput, latency, blocking behavior, allocation patterns.

```markdown
## Async Logger Throughput

~2 million logs/sec on modern hardware (single thread)
~5 million logs/sec with multiple threads

## Blocking

- Synchronous logger: blocks on write
- Async logger: non-blocking (queue-based), may block if queue is full
```

### 4.9 `examples/` directory

Minimal working examples. One file per example. Each example should be self-contained and compilable/runnable.

## 5. Registry Index (`index.json`)

### 5.1 Schema

```jsonc
{
  "schema": "libskills/v1",
  "version": 1,
  "updated_at": "2026-04-25T00:00:00Z",
  "skills": [
    {
      "key": "cpp/gabime/spdlog",
      "name": "spdlog",
      "language": "cpp",
      "tier": "tier1",
      "group": "main",
      "version": "1.14.2",
      "trust_score": 95,
      "tags": ["logging", "async", "thread-safe"],
      "summary": "Fast C++ logging library with async support"
    },
    {
      "key": "cpp/nlohmann/json",
      "name": "json",
      "language": "cpp",
      "tier": "tier1",
      "group": "main",
      "version": "3.11.3",
      "trust_score": 96,
      "tags": ["json", "serialization", "header-only"],
      "summary": "JSON for Modern C++"
    }
  ]
}
```

### 5.2 Distribution

The registry index is distributed as a **snapshot** (`registry.zip`), not a git clone. The CLI downloads and caches this snapshot.

- Snapshot URL: `https://github.com/LibSkills/registry/releases/latest/download/registry.zip`
- The CLI updates the index via `libskills update`

## 6. CLI Protocol

### 6.1 Commands

| Command | Description | MVP |
|---------|-------------|-----|
| `search <keyword>` | Fuzzy search index by name, tags, summary | ✅ |
| `get <path>[@version]` | Download skill to local cache | ✅ |
| `info <path>` | Show skill metadata | ✅ |
| `update` | Refresh registry index | ✅ |
| `cache` | Manage local cache | ✅ |
| `list` | List locally cached skills | ✅ |
| `doctor <path>` | Validate local skill | ❌ |
| `find <intent>` | Semantic/vector search | ❌ |
| `serve` | Start MCP/HTTP API | ❌ |

### 6.2 Local Cache Path

| Platform | Path |
|----------|------|
| Linux/macOS | `~/.libskills/` |
| Windows | `%APPDATA%/libskills/` |

### 6.3 AI Reading Protocol

When an AI agent consumes a skill, it MUST read files in this exact order:

1. `skill.json` — understand metadata, version, trust score
2. `overview.md` — understand what the library is
3. `api.md` — learn core API patterns
4. `pitfalls.md` — learn what NOT to do
5. `threading.md` — understand concurrency
6. `lifecycle.md` — understand init/shutdown
7. `memory.md` — understand resource management
8. `safety.md` — learn red lines
9. `performance.md` — understand characteristics
10. `examples/` — see working code

This order ensures that by the time the agent starts generating code, it has already learned what to avoid.

## 7. Semantic Search (Future)

### 7.1 Embedding Index

Each skill's `skill.json` includes tag summaries that can be embedded:

```
libskills find "high performance async logging"
→ cpp/gabime/spdlog (score: 0.92)
→ cpp/odyg/quill    (score: 0.85)
→ cpp/ms-gys/sinks  (score: 0.61)
```

### 7.2 Local Embedding Cache

```
~/.libskills/embeddings/
├── index.faiss
└── id_map.json
```

The `libskills update` command may optionally download pre-computed embeddings alongside the registry index.

## 8. MCP / HTTP API (Future)

```bash
libskills serve --port 8701
```

### Endpoints

```
GET  /v1/skills                           # List all skills
GET  /v1/skills/{language}/{author}/{name} # Get full skill
GET  /v1/skills/.../{section}             # Get specific section (e.g., pitfalls)
GET  /v1/search?q={keyword}               # Search
GET  /v1/find?q={intent}                  # Semantic search
POST /v1/skills                           # Submit a skill (Tier 2)
GET  /health                              # Health check
```

## 9. Skill Inheritance (Future)

Skills can inherit knowledge from parent skills to avoid duplication.

### 9.1 Inheritance Model

```
react-router@6.20
  inherits: react@18
```

When AI reads `react-router`, it also loads `react`'s knowledge first, then applies react-router-specific overrides.

### 9.2 Common Inheritance Chains

- `react-router` → `react`
- `redux-toolkit` → `redux` → `react`
- `grpc` (with multi-language bindings) → base `grpc` core

### 9.3 Skill Dependency Graph

If library A depends on library B, AI SHOULD load B's skill before A's.

```jsonc
{
  "dependencies": {
    "required": ["fmt"],
    "skills": ["cpp/fmtlib/fmt"]
  }
}
```

This ensures AI understands the full dependency chain before generating code.

## 10. Skill Types

Every skill should declare its type to help AI choose the right consumption strategy.

| Type | Example | AI Strategy |
|------|---------|-------------|
| `library` | spdlog, fmt | Load full API + pitfalls |
| `framework` | React, FastAPI | Load lifecycle + routing patterns |
| `sdk` | AWS SDK, Stripe | Load auth + error handling |
| `runtime` | Node.js, Deno | Load event loop + async patterns |
| `tooling` | CMake, Docker | Load configuration patterns |
| `middleware` | Express middleware | Load chain pattern |
| `database` | PostgreSQL driver | Load connection + query patterns |
| `network` | Boost.Asio, libcurl | Load async + error handling |
| `ui` | Dear ImGui, Qt | Load event loop + rendering patterns |
| `compiler` | Clang plugins | Load plugin lifecycle |

## 11. Skill Generator (Future)

```bash
libskills generate cpp/gabime/spdlog
```

Given a README, docs, and tests, automatically generate a skill scaffold.

### Input Sources
- README
- Official documentation
- Test files
- GitHub issues
- Benchmarks

### Output
- `skill.json` (metadata auto-filled)
- Directory structure with placeholders

## 12. Skill Linting (Future)

```bash
libskills lint cpp/gabime/spdlog
```

Checks:
- Missing required files
- Incomplete examples
- Token count outside 500–1500 range
- Missing tag entries
- Outdated version field

## 13. Completeness Score

Automatically calculated based on file presence:

| Files Present | Score |
|--------------|-------|
| 9 of 9 + examples | 100 |
| 7-8 of 9 + examples | 80–95 |
| 5-6 of 9 + examples | 60–75 |
| < 5 | < 50 |

Included in `skill.json` as `completeness`.

## 14. Compatibility Graph

```jsonc
{
  "compatibility": {
    "c++": ["17", "20", "23"],
    "compilers": ["clang>=16", "gcc>=11", "msvc>=2022"],
    "platforms": ["linux-x64", "macos-arm64", "windows-x64"]
  }
}
```

AI uses this to avoid suggesting incompatible compiler flags or platform-specific APIs.

## 15. Benchmark Data (Future)

Optional benchmark section in `performance.md`:

```markdown
## Benchmarks

| Config | Throughput | Latency p50 | Latency p99 |
|--------|-----------|-------------|-------------|
| Sync, single thread | 500k/s | 2µs | 10µs |
| Async, 4 threads | 2M/s | 0.5µs | 5µs |
| Flush every log | 10k/s | 100µs | 500µs |
```

## 16. Community Ratings (Future)

```jsonc
{
  "community_rating": {
    "reliability": 4.5,
    "hallucination_safety": 4.8,
    "thoroughness": 4.2
  },
  "votes": 128
}
```

## 17. Validation Rules

- Each markdown file must be 500–1500 tokens
- `pitfalls.md` is **required** (not optional)
- `safety.md` must contain at least 2 red-line entries
- `examples/` must contain at least 1 runnable example
- `trust_score` must be an integer 0–100
- `skill_version` must follow semver
- File names must be lowercase with `.md` extension
