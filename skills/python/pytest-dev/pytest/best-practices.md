# pytest — Best Practices

## Project Structure

```
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── models.py
│       └── services.py
└── tests/
    ├── conftest.py          # shared fixtures
    ├── test_models.py
    ├── test_services.py
    └── fixtures/
        ├── __init__.py      # conftest alternative for complex projects
        └── data_helpers.py
```

## Fixture Organization

- **Put shared fixtures in `conftest.py`** at the relevant directory level
- **Use scope wisely**: `function` for mutable state, `module` for DB connections, `session` for immutable config
- **Name fixtures descriptively** — the fixture name is how it's injected
- **Use `conftest.py` layers** — fixtures in parent directories are available in child directories

```python
# tests/conftest.py — top-level, available everywhere
@pytest.fixture
def db():
    conn = create_test_db()
    yield conn
    conn.close()
```

```python
# tests/api/conftest.py — only available in tests/api/
@pytest.fixture
def api_client(db):
    return TestClient(app, db)
```

## Test Isolation

- Each test should set up its own data or use fixtures
- Clean up after yourself — use fixture teardown (yield) or autouse fixtures
- Never depend on other tests having run

## Using Marks Effectively

```python
# Register custom marks in pyproject.toml or pytest.ini
# [tool.pytest.ini_options]
# markers = [
#     "slow: marks tests as slow (deselect with '-m \"not slow\"')",
#     "integration: marks integration tests",
# ]
@pytest.mark.slow
def test_heavy_computation():
    pass

@pytest.mark.integration
def test_db_integration(db):
    pass

# Run: pytest -m "not slow"
# Run: pytest -m "integration"
```

## Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
markers =
    slow: marks tests as slow
    integration: marks integration tests
filterwarnings =
    error
    ignore::DeprecationWarning
```

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
markers = { slow = "marks tests as slow", integration = "marks integration tests" }
```

## Assertion Best Practices

```python
# Use pytest.approx for floats
import pytest
assert result == pytest.approx(3.14, rel=1e-3)

# Use pytest.raises for exceptions
with pytest.raises(ValueError, match="invalid input"):
    parse_input("bad")

# Use pytest.warns for warnings
import warnings
with pytest.warns(DeprecationWarning):
    deprecated_function()
```
