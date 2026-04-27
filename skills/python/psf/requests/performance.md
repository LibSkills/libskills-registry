# requests — Performance

## Connection Pooling

The single biggest performance improvement: use a `Session` instead of bare function calls.

```python
# BAD: ~100ms per request (new TCP + TLS per call)
for url in urls:
    requests.get(url, timeout=5)

# GOOD: ~5ms per request after initial connection (keep-alive)
with requests.Session() as s:
    for url in urls:
        s.get(url, timeout=5)
```

A Session reuses the underlying TCP connection and TLS session, avoiding the 3-way handshake and TLS negotiation on subsequent requests to the same host.

## Streaming Large Responses

For responses larger than a few MB, use `stream=True` to avoid buffering the entire body in memory.

```python
with requests.get(url, stream=True, timeout=30) as r:
    r.raise_for_status()
    with open("output.dat", "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
```

- `chunk_size=8192` is a good default
- `r.iter_content()` yields raw bytes
- `r.iter_lines()` yields decoded text lines (slower, only for text)

## Gzip/Deflate Compression

requests automatically decompresses gzip and deflate responses. Add `Accept-Encoding` to request compressed bodies:

```python
headers = {"Accept-Encoding": "gzip, deflate"}
r = requests.get(url, headers=headers, timeout=5)
# r.content is automatically decompressed
```

## Concurrent Requests

requests is synchronous. For concurrency, use:

| Approach | Throughput | Complexity |
|----------|-----------|------------|
| `ThreadPoolExecutor` + Session per thread | Moderate | Low |
| `asyncio` + `httpx` | High | Medium |
| `asyncio` + `aiohttp` | Highest | Medium |
| `multiprocessing` + Session per process | Very high | High |

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(url):
    with requests.Session() as s:
        return s.get(url, timeout=5)

with ThreadPoolExecutor(max_workers=10) as pool:
    futures = [pool.submit(fetch, url) for url in urls]
    for future in as_completed(futures):
        result = future.result()
```
