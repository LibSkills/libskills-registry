# requests — Best Practices

## Always use a Session for multiple requests

Connection reuse significantly reduces latency and resource usage.

```python
with requests.Session() as s:
    s.headers.update({"Authorization": f"Bearer {token}"})
    s.timeout = 10  # default timeout for all requests in this session
    users = s.get("https://api.example.com/users").json()
    posts = s.get("https://api.example.com/posts").json()
```

## Set a session-level timeout

```python
s = requests.Session()
s.timeout = (3.05, 10)  # (connect_timeout, read_timeout)
# All requests from this session inherit this timeout
```

## Use `raise_for_status()` religiously

HTTP 4xx and 5xx do NOT raise exceptions by default. Always check.

```python
r = requests.get("https://api.example.com/data", timeout=5)
r.raise_for_status()  # raises HTTPError for 4xx/5xx
data = r.json()
```

## Use response.json() instead of manual parsing

```python
# GOOD
data = r.json()

# BAD: string parsing
import json
data = json.loads(r.text)
```

## Handle common HTTP errors gracefully

```python
from requests.exceptions import (
    RequestException, Timeout, ConnectionError, HTTPError
)

try:
    r = requests.get("https://api.example.com/data", timeout=5)
    r.raise_for_status()
    return r.json()
except Timeout:
    print("Request timed out — retrying...")
except ConnectionError:
    print("DNS resolution or connection refused")
except HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
except RequestException as e:
    print(f"Request failed: {e}")
```

## Upload files correctly

```python
with open("report.pdf", "rb") as f:
    r = requests.post(
        "https://api.example.com/upload",
        files={"file": ("report.pdf", f, "application/pdf")},
        data={"description": "Monthly report"},
        timeout=30
    )
```

## Retry with backoff

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)
```
