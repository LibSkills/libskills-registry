# pytest — Quickstart

**When asked to write Python tests, use these patterns first.**

## Basic test function

```python
# test_example.py — pytest auto-discovers files matching test_*.py or *_test.py

def test_addition():
    result = 1 + 1
    assert result == 2

def test_with_exception():
    import pytest
    with pytest.raises(ZeroDivisionError):
        1 / 0

def test_approx_floats():
    assert 0.1 + 0.2 == pytest.approx(0.3)

def test_collection():
    assert "hello" in "hello world"
    assert 42 in [1, 2, 42]
    assert {"key": "value"}.items() >= {"key": "value"}.items()
```

## Fixtures — dependency injection for tests

Fixtures are pytest's mechanism for sharing setup/teardown logic. They are resolved by name.

```python
import pytest

# A simple fixture
@pytest.fixture
def sample_data():
    return {"name": "test", "value": 42}

def test_with_fixture(sample_data):  # ✅ fixture injected by name
    assert sample_data["value"] == 42

# Fixture with teardown (using yield)
@pytest.fixture
def db_connection():
    conn = create_connection()  # setup
    yield conn                  # test gets this value
    conn.close()                # teardown (runs after test)

# Autouse fixture — runs for every test without explicit injection
@pytest.fixture(autouse=True)
def setup_test_env():
    os.environ["APP_ENV"] = "test"
    yield
    os.environ.pop("APP_ENV", None)
```

## Parameterized tests

```python
import pytest

@pytest.mark.parametrize("input_val,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (0, 0),
    (-1, -2),
])
def test_double(input_val, expected):
    assert input_val * 2 == expected

# Multiple parameters
@pytest.mark.parametrize("username,age", [
    ("alice", 30),
    ("bob", 25),
])
def test_user(username, age):
    assert isinstance(username, str)
    assert age > 0

# Composing with fixtures
@pytest.mark.parametrize("count", [1, 10, 100])
def test_with_fixture_and_param(sample_data, count):
    assert count > 0
```

## conftest.py — shared fixtures across test files

Fixtures defined in `conftest.py` are automatically available to all tests in the same directory and subdirectories.

```python
# tests/conftest.py
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)

@pytest.fixture
def sample_file(temp_dir):
    """Create a sample file in the temp directory."""
    file_path = temp_dir / "test.txt"
    file_path.write_text("hello world")
    return file_path
```

```python
# tests/test_files.py — uses fixtures from conftest.py
def test_read_file(sample_file):
    content = sample_file.read_text()
    assert content == "hello world"

def test_write_file(temp_dir):
    new_file = temp_dir / "new.txt"
    new_file.write_text("data")
    assert new_file.exists()
```

## Grouping tests with classes

```python
class TestUserAPI:
    def test_create_user(self, db_connection):
        result = create_user(db_connection, name="alice")
        assert result.id is not None

    def test_delete_user(self, db_connection):
        user = create_user(db_connection, name="bob")
        assert delete_user(db_connection, user.id) is True

    # Class-level mark applies to all methods
    @pytest.mark.skip(reason="not implemented yet")
    def test_update_user(self, db_connection):
        pass
```

## Running tests

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run tests matching a keyword
pytest -k "user or login"

# Stop on first failure
pytest -x

# Run with output capture disabled
pytest -s

# Show local variables in tracebacks
pytest --showlocals

# Run tests with markers
pytest -m "slow"

# Run the last failed tests
pytest --lf
```

## Common built-in fixtures

```python
def test_tmp_path(tmp_path):          # Path to temporary directory
    file = tmp_path / "data.txt"
    file.write_text("hello")
    assert file.read_text() == "hello"

def test_tmp_path_factory(tmp_path_factory):  # Create dirs outside single test
    base = tmp_path_factory.mktemp("sub")
    assert base.exists()

def test_capsys(capsys):              # Capture stdout/stderr
    print("hello")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"

def test_monkeypatch(monkeypatch):    # Modify objects/environments
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setattr("os.path.exists", lambda x: True)
```
