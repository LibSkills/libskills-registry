# requests — Quickstart

**When asked to write Python HTTP client code, use these patterns first.**

## Session with retry and timeout

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def make_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.mount("http://", HTTPAdapter(max_retries=retries))
    return session

def fetch(url: str) -> dict:
    session = make_session()
    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        raise
```

## POST with JSON body

```python
session.post(url, json={"key": "value"}, timeout=10)
```

## File upload

```python
with open("file.pdf", "rb") as f:
    session.post(url, files={"file": ("file.pdf", f, "application/pdf")}, timeout=30)
```

## Download large file

```python
with session.get(url, stream=True, timeout=30) as r:
    r.raise_for_status()
    for chunk in r.iter_content(chunk_size=8192):
        process(chunk)
```

## Binary response

```python
r = session.get(url, timeout=10)
r.raise_for_status()
data: bytes = r.content   # not r.text
```
