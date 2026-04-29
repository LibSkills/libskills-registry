# pytest — Lifecycle

## Test Collection Phase

1. pytest scans configured `testpaths` for files matching `test_*.py` or `*_test.py`
2. Within each file, discovers functions matching `test_*` and classes matching `Test*`
3. Collects fixtures, marks, and parametrizations
4. Builds the test execution tree (respects scope and dependency ordering)

## Test Execution Phase

For each test function:

1. **Setup** — resolve fixture dependencies (breadth-first, respecting scope)
2. **Call** — execute the test function with injected fixtures
3. **Assert** — evaluate assertions with rich diff output on failure
4. **Teardown** — execute fixture cleanup in reverse dependency order

## Fixture Lifecycle

```python
@pytest.fixture(scope="session")
def config():
    # setup: runs once per session
    yield
    # teardown: runs once after all tests

@pytest.fixture(scope="module")
def db(config):
    # setup: runs once per test module
    yield
    # teardown: runs after last test in module

@pytest.fixture(scope="function")
def item(db):
    # setup: runs before each test
    yield
    # teardown: runs after each test
```

## Autouse Fixtures

`autouse=True` fixtures run automatically without explicit injection. They follow the same lifecycle rules.

```python
@pytest.fixture(autouse=True)
def mock_time(monkeypatch):
    """Mock time for all tests in this module."""
    monkeypatch.setattr(time, "time", lambda: 1000.0)
```

## Cache Plugin

pytest caches the last failed test IDs. Use `--lf` to run only the last failed tests. Use `--ff` to run failed tests first then the rest.
