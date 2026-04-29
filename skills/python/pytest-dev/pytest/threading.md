# pytest — Threading & Concurrency

## Single-Threaded by Default

pytest runs tests sequentially in a single process by default. Each test function is isolated but fixtures may be shared (depending on scope).

## Fixture Thread Safety

Function-scoped fixtures are safe by default since each test gets its own instance. However:

- **Session/module-scoped fixtures** shared across tests are NOT thread-safe when using `pytest-xdist`
- **File handles, DB connections, and mutable objects** in shared-scope fixtures need synchronization

```python
# Thread-safe session fixture with lock
import threading
_lock = threading.Lock()

@pytest.fixture(scope="session")
def shared_resource():
    return {"data": []}

def test_thread_safe(shared_resource):
    with _lock:
        shared_resource["data"].append(1)  # ✅ explicit locking
```

## pytest-xdist Concurrency Model

- `-n auto` spawns workers as child processes (not threads)
- Each worker runs tests independently with its own memory space
- Session-scoped fixtures run once per worker — **not** truly shared
- File-based caches (like DB files) need separate paths per worker

```python
import os
import pytest

@pytest.fixture(scope="session")
def worker_id():
    """Get unique worker ID for xdist."""
    return os.environ.get("PYTEST_XDIST_WORKER", "master")

@pytest.fixture
def db_path(tmp_path, worker_id):
    """Unique DB path per worker."""
    return tmp_path / f"test_{worker_id}.db"  # ✅ no collisions
```

## Async Tests

For async code, use `pytest-asyncio`:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await fetch_data()
    assert result is not None
```

## Process-Safe Resources

When using xdist, ensure resources (ports, files, DBs) don't collide:

```python
@pytest.fixture(scope="session")
def free_port():
    """Get a unique port for each worker."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]
```
