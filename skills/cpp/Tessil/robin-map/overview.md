# Overview

The `tsl::robin_map` library provides fast hash map and hash set implementations using open-addressing with Robin Hood hashing and backward shift deletion. It is a header-only library that offers four main classes: `tsl::robin_map`, `tsl::robin_set`, `tsl::robin_pg_map`, and `tsl::robin_pg_set`. The first two use a power-of-two growth policy for maximum speed, while the prime growth policy variants (`_pg`) handle poor hash functions better.

Use this library when you need a high-performance hash table that outperforms `std::unordered_map` in most scenarios, especially for lookups and insertions. It is particularly suitable for:
- Performance-critical applications where hash table operations are a bottleneck
- Storing move-only or non-default-constructible keys/values
- Situations requiring heterogeneous lookups (e.g., searching with `std::string_view` instead of `std::string`)
- Serialization/deserialization of hash table contents

Do NOT use this library when:
- You need stable iterators across insertions (all modifying operations invalidate iterators)
- You require bucket-based operations like `bucket_size()` or `bucket()`
- Your value types are not swappable or not copy/move constructible
- You need the strong exception guarantee with types that throw on swap or move

Key design features include:
- Open-addressing with Robin Hood hashing for cache-friendly memory access
- Backward shift deletion to maintain performance after removals
- Support for storing hash values alongside keys for faster rehashing
- Precalculated hash lookups for repeated searches with the same key
- Serialization support for saving/loading map contents