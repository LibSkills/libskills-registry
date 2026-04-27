# requests — Pitfalls

## Do NOT forget to set a timeout

requests has **no default timeout**. A request can hang indefinitely if the server doesn't respond.

```python
# BAD: hangs forever if server is unresponsive
response = requests.get("https://api.example.com/data")

# GOOD: always set timeout
response = requests.get("https://api.example.com/data", timeout=30)  # (connect, read)
```

## Do NOT use bare get/post without a Session

Each call to `requests.get()` creates a new connection. For multiple requests to the same host, use a `Session` to reuse connections (HTTP keep-alive).

```python
# BAD: new TCP+TLS handshake every time
for i in range(100):
    requests.get(f"https://api.example.com/item/{i}", timeout=5)

# GOOD: connection reuse
with requests.Session() as s:
    for i in range(100):
        s.get(f"https://api.example.com/item/{i}", timeout=5)
```

## Do NOT forget to close responses or use a context manager

Response bodies are buffered by default for small responses. For large responses, the underlying connection isn't released back to the pool until the body is fully read or the response is closed.

```python
# BAD: connection leaks (large responses)
r = requests.get("https://example.com/large-file", stream=True, timeout=30)
# ... use r.raw ... but never close

# GOOD: context manager
with requests.get("https://example.com/large-file", stream=True, timeout=30) as r:
    for chunk in r.iter_content(chunk_size=8192):
        process(chunk)
```

## Do NOT confuse `json=` with `data=`

`json=` serializes a dict to JSON and sets `Content-Type: application/json`. `data=` sends raw form data or a string.

```python
# BAD: sends form-encoded, not JSON
requests.post("https://api.example.com", data={"key": "value"})
# Server receives: key=value (form-encoded)

# GOOD: sends JSON
requests.post("https://api.example.com", json={"key": "value"}, timeout=5)
# Server receives: {"key": "value"} (JSON)
```

## Do NOT set `verify=False`

Disabling SSL verification exposes you to MITM attacks. If you must use a custom CA, use `verify="/path/to/ca-bundle.crt"`.

```python
# BAD: vulnerable to MITM
requests.get("https://api.example.com", verify=False)

# GOOD: use proper CA
requests.get("https://api.example.com", verify="/etc/ssl/certs/ca-certificates.crt", timeout=5)
```

## Do NOT use `r.text` for binary responses

`r.text` decodes the response body using the detected encoding. For binary data (images, files, protobuf), use `r.content` (bytes) instead.

```python
# BAD: corrupts binary data
r = requests.get("https://example.com/image.png", timeout=5)
with open("image.png", "w") as f:
    f.write(r.text)  # decoding may modify bytes

# GOOD: raw bytes
r = requests.get("https://example.com/image.png", timeout=5)
with open("image.png", "wb") as f:
    f.write(r.content)
```
