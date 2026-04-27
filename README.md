# libskills-registry

**Aggregated skill index — 6 Tier 1 skills across C++, Rust, and Python.**

This repository contains the aggregation index (`index.json`) and skill files served to `libskills search`, `libskills find`, and `libskills get`.

## Skills

| Key | Language | Library | Risk |
|-----|----------|---------|------|
| `cpp/gabime/spdlog` | C++ | spdlog — Fast logging library | medium |
| `cpp/fmtlib/fmt` | C++ | {fmt} — Modern formatting library | low |
| `rust/serde-rs/serde` | Rust | serde — Serialization framework | low |
| `rust/tokio-rs/tokio` | Rust | tokio — Async runtime | high |
| `python/psf/requests` | Python | requests — HTTP client | medium |
| `python/tiangolo/fastapi` | Python | FastAPI — Web framework | medium |

## Structure

```
skills/
├── cpp/{author}/{name}/
│   ├── skill.json
│   ├── overview.md
│   ├── pitfalls.md
│   ├── safety.md
│   ├── lifecycle.md
│   ├── threading.md
│   ├── best-practices.md
│   ├── performance.md
│   └── examples/
├── rust/
├── python/
├── go/
└── js/
```

Skills use a flat structure with **P0/P1/P2/P3 file priorities** instead of tier1/tier2 subdirectories. Each skill carries its own `tier` and `group` fields in `skill.json`.

## Index

`index.json` is the master aggregration index. Entries reference both repo-hosted skills (`repo_skill: true`) and registry-only entries. The index is consumed by `libskills update`.

## Discovery Sources

The aggregation registry discovers skills via:

1. **GitHub code search** for `path:.libskills/skill.json`
2. **GitHub topic** `libskills` on repositories
3. **Manual PR submissions** to this repository

## Contributing

1. Add `.libskills/` to your library's repository (recommended)
2. OR submit a PR to this repo adding your skill to `skills/` and `index.json`

See [CONTRIBUTING.md](https://github.com/LibSkills/libskills-docs/blob/main/CONTRIBUTING.md) for full guidelines.

## License

Apache 2.0
