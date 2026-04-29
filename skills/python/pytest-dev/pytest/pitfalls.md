# pytest — Pitfalls

Common mistakes that cause flaky tests, state pollution, or confusing failures.

## Fixture scope set wrong — state pollution across tests

Using `scope="session"` or `scope="module"` with mutable objects leads to test-order-dependent failures.

```python
# BAD: session-scoped mutable list — tests interfere
@pytest.fixture(scope="session")
def data():
    return []

def test_add_item(data):
    data.append("item1")
    assert len(data) == 1  # ✅ passes first time (test order 1)

def test_another(data):
    assert len(data) == 1  # ❌ FAILS when run after test_add_item — data already has 2 items
```

```python
# GOOD: function scope — fresh per test
@pytest.fixture
def data():
    return []  # fresh empty list every test

# Or: use session scope for immutable data
@pytest.fixture(scope="session")
def api_base_url():
    return "https://api.example.com"  # ✅ immutable string, safe to share
```

## Fixture dependencies — order matters for cleanup

When fixtures depend on each other, cleanup happens in reverse order. This matters for scoped resources.

```python
# BAD: module-level resource used across test modules
@pytest.fixture(scope="module")
def db():
    conn = create_db()
    yield conn
    conn.close()  # cleanup after ALL tests in module

@pytest.fixture(scope="module")
def table(db):
    db.execute("CREATE TABLE test (id int)")
    yield
    db.execute("DROP TABLE test")

def test_insert(table, db):  # table fixture depends on db
    pass
# Cleanup order: table cleanup first, then db cleanup ✅ correct
```

## tmp_path vs pathlib confusion

`tmp_path` returns a `pathlib.Path` object, not a string. Mixing string and Path operations causes subtle bugs.

```python
# BAD: mixing str and Path
def test_file(tmp_path):
    filepath = str(tmp_path) + "/data.txt"  # ❌ /tmp/pytest-xxx/data.txt works
    with open(filepath, "w") as f:           # but fragile
        f.write("data")
    assert Path(filepath).read_text() == "data"

# GOOD: pure pathlib
def test_file(tmp_path):
    filepath = tmp_path / "data.txt"         # ✅ proper Path join
    filepath.write_text("data")
    assert filepath.read_text() == "data"

# GOOD: pure str with os.path.join
def test_file(tmp_path):
    filepath = os.path.join(str(tmp_path), "data.txt")  # ✅ if you must use str
```

## monkeypatch not restored after test

`monkeypatch` changes persist if not properly scoped or if an exception skips teardown.

```python
# BAD: patching objects without context manager
def test_something(monkeypatch):
    monkeypatch.setattr("os.path.exists", lambda x: True)
    # if this raises exception, the patch is NOT reverted → affects other tests!
    result = do_something()
    assert result is True
    # Patch reverted after test returns ✅ but only if no exception

# BAD: module-level patching without context manager (test order dependent)
@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "testing")
    # No yield, no explicit undo — but monkeypatch fixture handles it ✅

# BETTER: explicit scoping for complex patches
@pytest.fixture
def mock_db(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("mymodule.db", mock)
    return mock
```

## Parametrize with too many or too large datasets

Running hundreds of parametrized cases can slow down test runs and consume memory.

```python
# BAD: 10000 parametrized cases — slow, hard to maintain
@pytest.mark.parametrize("i", range(10000))
def test_large_param(i):
    assert i * 2 == i * 2  # 10000 tests generated!

# GOOD: use pytest.mark.parametrize with a reasonable count
@pytest.mark.parametrize("i", range(20))
def test_reasonable_param(i):
    assert i * 2 == i * 2

# GOOD: use indirection — test logic, not data size
def test_algorithm(matcher):
    # Test the algorithm, not 10000 inputs
    for i in range(10000):
        assert matcher.match(i) is True
```

## Using bare `assert` for floating point comparison

```python
# BAD: floating point precision
def test_float():
    assert 0.1 + 0.2 == 0.3  # ❌ FAILS due to floating point

# GOOD: use pytest.approx
def test_float():
    assert 0.1 + 0.2 == pytest.approx(0.3)

# GOOD: with tolerance
def test_float_tolerance():
    assert 0.1 + 0.2 == pytest.approx(0.3, rel=1e-9)
```

## Forgetting autouse for cleanup-only fixtures

```python
# BAD: fixture declared but never injected → cleanup never runs
@pytest.fixture
def cleanup_temp():
    yield
    shutil.rmtree("/tmp/test-artifacts")

def test_no_cleanup():
    pass  # ❌ cleanup_temp never runs

# GOOD: autouse to ensure cleanup
@pytest.fixture(autouse=True)
def cleanup_temp():
    yield
    shutil.rmtree("/tmp/test-artifacts", ignore_errors=True)  # ✅ always runs

# GOOD: inject explicitly
def test_with_cleanup(cleanup_temp):
    pass  # ✅ fixture runs because it's injected
```
