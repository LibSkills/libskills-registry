# Overview

redis/redis-py (specifically the C++ wrapper redis-plus-plus) is a high-performance C++ client library for Redis, providing both synchronous and asynchronous APIs. It wraps the Redis protocol with type-safe C++ interfaces for all Redis data structures including strings, hashes, lists, sets, sorted sets, and streams.

**When to use:**
- Building C++ applications that need fast in-memory caching
- Implementing real-time data structures like queues, leaderboards, or session stores
- Applications requiring Redis pub/sub messaging
- Systems needing atomic operations with transactions and Lua scripting

**When NOT to use:**
- For simple key-value storage where a database like SQLite suffices
- When you need complex querying capabilities (Redis is not a query engine)
- For data that requires ACID compliance with rollback guarantees
- When memory constraints are critical (Redis stores data in RAM)

**Key design features:**
- Connection pooling with automatic reconnection
- Pipeline and transaction support for batching operations
- Thread-safe connection management
- Support for Redis Cluster and Sentinel
- Both synchronous and asynchronous (with event loop) APIs