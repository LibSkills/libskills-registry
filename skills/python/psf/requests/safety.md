# requests — Safety

Red lines — conditions that must NEVER occur.

## NEVER disable SSL verification in production

`verify=False` disables TLS certificate validation, making the connection vulnerable to man-in-the-middle attacks. Use `verify="/path/to/custom-ca.pem"` if you need a custom CA.

```python
# NEVER DO THIS IN PRODUCTION
requests.get("https://api.example.com", verify=False, timeout=5)
```

## NEVER make requests from a Session across threads

`requests.Session` is NOT thread-safe. Its connection pool, cookie jar, and header state are not synchronized. Create one Session per thread.

```python
# BAD: data races on session state
session = requests.Session()
def worker():
    session.get("https://api.example.com")  # concurrent access — undefined
threading.Thread(target=worker).start()
threading.Thread(target=worker).start()

# GOOD: one session per thread, or use locks
```

## NEVER pass user input directly as a URL without validation

requests follows redirects automatically. An attacker-controlled URL could redirect to internal services (SSRF). Use `urllib.parse` to validate the host before making the request.

```python
# BAD: SSRF vulnerability
requests.get(user_input_url, timeout=5)
# user_input_url = "http://169.254.169.254/metadata" (AWS metadata endpoint)
```

## NEVER deserialize an HTTP response body without checking status

A 4xx or 5xx response may still have a valid JSON body — but it's an error response, not the expected data. Always check `r.raise_for_status()` before processing the body.

```python
# BAD: silently processes error response
r = requests.get("https://api.example.com/data", timeout=5)
data = r.json()
process(data)  # may process error message as real data

# GOOD: check status first
r = requests.get("https://api.example.com/data", timeout=5)
r.raise_for_status()
data = r.json()
```

## NEVER send secrets in URL query strings

URLs are logged by servers, proxies, and browsers. API keys, tokens, and passwords in query strings are exposed in logs. Always use headers (`Authorization`, `X-API-Key`) or request body for secrets.

```python
# BAD: secret in URL
requests.get(f"https://api.example.com/data?api_key={secret}", timeout=5)

# GOOD: secret in header
requests.get("https://api.example.com/data", headers={"X-API-Key": secret}, timeout=5)
```
