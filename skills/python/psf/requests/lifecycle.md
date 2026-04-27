# requests — Lifecycle

## Session Lifecycle

A `Session` maintains a connection pool, cookie jar, and default headers. Always use a context manager (`with` statement) to ensure proper cleanup.

```python
# Recommended: Session with context manager
with requests.Session() as session:
    session.headers.update({"User-Agent": "my-app/1.0"})
    session.auth = ("user", "pass")
    r = session.get("https://api.example.com/data", timeout=10)
    # Session automatically closed on exit

# Alternative: manual close
session = requests.Session()
try:
    r = session.get("https://api.example.com/data", timeout=10)
finally:
    session.close()
```

## Response Lifecycle

Small responses buffer the entire body in memory. Large or streaming responses must be consumed and closed.

```python
# Stream large response
with requests.get("https://example.com/large-file", stream=True, timeout=30) as r:
    r.raise_for_status()
    with open("output.dat", "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
# Response and connection returned to pool when context exits
```

## Connection Pooling

- `Session` maintains a `urllib3` connection pool (default: 10 connections per host)
- Connections are reused for the same `(scheme, host, port)` tuple
- Idle connections are kept alive for HTTP keep-alive
- Pool is drained when the Session is closed

## Cookie Persistence

```python
session = requests.Session()
session.cookies.set("session_id", "abc123")
# Subsequent requests to same domain include this cookie automatically
r = session.get("https://api.example.com/profile")
```
