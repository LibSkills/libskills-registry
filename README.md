# libskills-registry

**Aggregated skill index — 58 skills across C++, Python, Go, and Rust.**

This repository contains the aggregation index (`index.json`) and skill files served to `libskills search`, `libskills find`, `libskills get`, and the MCP server `libskills-mcp`.

## Stats

| Language | Skills | Status |
|----------|:------:|:------:|
| **C++** | 28 | 🔄 50 target (22 remaining) |
| **Python** | 10 | ✅ Target met |
| **Go** | 10 | ✅ Target met |
| **Rust** | 10 | ✅ Target met |
| **Total** | **58** | 🎯 80 target |

Skills are auto-generated via the [v2 pipeline](https://github.com/LibSkills/libskills-docs) and curated for quality (minimum 7.5/10 score).

## Structure

```
skills/
├── cpp/{author}/{name}/
│   ├── skill.json
│   ├── quickstart.md      (P0)
│   ├── overview.md         (P0)
│   ├── pitfalls.md         (P0)
│   ├── safety.md           (P0)
│   ├── best-practices.md   (P1)
│   ├── lifecycle.md        (P1)
│   ├── performance.md      (P2)
│   ├── threading.md        (P2)
│   └── examples/
├── rust/
├── python/
└── go/
```

Skills use a **P0/P1/P2/P3 file priority system** instead of tier1/tier2 subdirectories. Each skill carries its own `tier` and `group` fields in `skill.json`.

## Tools

- **`skills` CLI**: `skills search`, `skills find`, `skills get`, `skills section`, `skills list`
- **`libskills-mcp` MCP server**: Exposes `get_skill`, `get_section`, `search_skills`, `find_skills` tools
- **Batch generation pipeline**: `/tmp/genproto/v2/` — Daily cron at 11:00/18:00 CST

## Index

`index.json` is the master aggregation index. It is consumed by `libskills update`, `skills search`, and the MCP server.

## Discovery Sources

The aggregation registry discovers skills via:

1. **GitHub code search** for `path:.libskills/skill.json`
2. **GitHub topic** `libskills` on repositories
3. **Manual PR submissions** to this repository
4. **Auto-generation pipeline** from the LibSkills ecosystem

## License

Apache 2.0
