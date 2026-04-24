# libskills-registry

**Official registry of library skills — Tier 1 & Tier 2 knowledge for C++, Rust, Python and more.**

This repository contains the skill files indexed by `libskills search` and downloaded by `libskills get`.

## Structure

```
cpp/
├── gabime/
│   └── spdlog/       # Fast C++ logging library
│       ├── skill.json
│       ├── tier1/
│       │   ├── overview.md
│       │   ├── api.md
│       │   ├── pitfalls.md
│       │   ├── threading.md
│       │   ├── lifecycle.md
│       │   ├── memory.md
│       │   ├── safety.md
│       │   ├── performance.md
│       │   └── examples/
│       └── tier2/
└── nlohmann/
    └── json/         # JSON for Modern C++
rust/
└── ...
python/
└── ...
```

## Convention

```
{language}/{author}/{name}/
```

- `tier1/` — Official, reviewed skills
- `tier2/` — Community-submitted skills

## Contributing

Submit a PR to add or update a skill. See the full specification at [LibSkills/spec](https://github.com/LibSkills/libskills-schema).

## License

Apache 2.0
