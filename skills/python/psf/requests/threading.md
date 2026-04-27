# requests — Threading

**requests is synchronous and NOT thread-safe for Session objects.**

## Session Thread Safety

`requests.Session` is NOT thread-safe. Its connection pool, cookie jar, and internal state are not synchronized. Concurrent access from multiple threads causes data races.

```python
# BAD: session shared across threads
session = requests.Session()
with ThreadPoolExecutor() as pool:
    pool.map(lambda url: session.get(url, timeout=5), urls)

# GOOD: one session per thread
def fetch(url):
    with requests.Session() as s:
        return s.get(url, timeout=5)

with ThreadPoolExecutor() as pool:
    results = pool.map(fetch, urls)
```

## Per-Request Safety

Individual `requests.get()` / `requests.post()` calls (without Session) are thread-safe because each call creates a new connection. This is less efficient but safe.

```python
# Thread-safe but inefficient (no connection reuse)
def fetch(url):
    return requests.get(url, timeout=5)
```

## Async/Concurrent Alternatives

requests is fundamentally blocking. For concurrent HTTP, use:

| Library | Model | When |
|---------|-------|------|
| `httpx` | Async + sync | Modern replacement, async/await support |
| `aiohttp` | Async only | High-concurrency async HTTP |
| `requests` + `ThreadPoolExecutor` | Sync with threads | Simpler code, moderate concurrency |
| `requests-futures` | Sync with futures | Backward-compatible async wrapper |

## Timeout and Threads

When using threads, ensure every request has a timeout. A thread without a timeout is a leaked resource that blocks the thread pool indefinitely.
