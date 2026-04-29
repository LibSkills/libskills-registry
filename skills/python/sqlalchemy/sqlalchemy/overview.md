# SQLAlchemy — Overview

**SQLAlchemy** is the most widely used SQL toolkit and Object-Relational Mapper for Python. v2.0 introduces a unified async/sync API, native support for `select()` statements as core query API, and improved type annotations.

## When to Use

- Any Python application that needs a relational database
- Building data-access layers with complex relationships and joins
- Async applications with PostgreSQL (asyncpg) or SQLite (aiosqlite)
- Migrating from raw SQL to a typed, composable query builder

## When NOT to Use

- Simple key-value workloads (use redis)
- Ultra-high-throughput OLTP with simple queries (raw asyncpg may be 2-3x faster)
- Embedded / low-memory environments where SQLAlchemy's import overhead matters (import takes ~200ms)
- When you only need bulk inserts with zero ORM overhead (use `sqlalchemy.dialects.postgresql.insert` with `executemany`)

## Key Design (2.0 Style)

- **Core vs ORM**: Core is a SQL expression builder; ORM builds on Core with identity maps, unit of work, and relationship loading
- **Declarative models**: Define tables and ORM classes together via `mapped_column()` and `Mapped[]` types
- **`select()` is the one true way**: v2.0 deprecates the old `Query` API. All queries use `select(Model).where(...)`
- **Async supported natively**: `AsyncSession`, `AsyncEngine`, `async def` — no more `greenlet` hacks
- **Session as a transaction scope**: A Session wraps a database transaction; commit on success, rollback on error
