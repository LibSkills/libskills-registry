# pytest — Safety

Red lines — conditions that must NEVER occur.

## NEVER put mutable state in a `session`-scoped fixture

Session-scoped fixtures are created once and shared across ALL tests. Mutable objects (lists, dicts, sets) accumulate changes from one test to the next, causing non-deterministic failures.

```python
# NEVER — session scope with mutable dict
@pytest.fixture(scope="session")
def config():
    return {}  # ❌ tests mutate this and interfere with each other

# NEVER — session scope with mutable list accumulating state
@pytest.fixture(scope="session")
def users():
    return ["alice", "bob"]

def test_add_user(users):
    users.append("charlie")  # ❌ pollutes next test
    assert len(users) == 3
```

```python
# ALWAYS — use module or function scope for mutable state
@pytest.fixture(scope="module")
def config():
    db = setup_database()
    yield db
    db.close()

# ALWAYS — session scope for immutable data only
@pytest.fixture(scope="session")
def api_token():
    return "test-token-abc-123"  # ✅ immutable string, safe

# ALWAYS — session scope with factory function
@pytest.fixture(scope="session")
def make_user():
    """Create a fresh user each time."""
    def _make(name):
        return User(name=name, id=uuid4().hex)
    return _make  # ✅ call the factory per test
```

## NEVER use `pytest.skip()` or `pytest.fail()` inside a fixture setup

Calling `pytest.skip()` or `pytest.fail()` in fixture setup is confusing because the skip/fail message is attributed to the test, not the fixture, and skip/fail inside yield fixtures prevents teardown from running.

```python
# NEVER — skip inside yield fixture prevents teardown
@pytest.fixture
def database():
    if not db_available():
        pytest.skip("database not available")  # ❌ teardown after yield NEVER runs
    yield setup_connection()
    teardown_connection()
```

```python
# ALWAYS — use try/finally or separate the check
@pytest.fixture
def database():
    if not db_available():
        pytest.skip("database not available")
    conn = setup_connection()
    yield conn
    teardown_connection()

# ALWAYS — use pytest.raises from test, not fixture
def test_database(database):
    if not database:
        pytest.skip("no connection")
    assert database.query("SELECT 1") == 1
```

## NEVER share `tmp_path` or `tmp_path_factory` across sessions

These fixtures create temporary directories that are cleaned up after each test. Storing references across tests leads to `FileNotFoundError`.

```python
# NEVER — storing paths across tests
paths = []

@pytest.fixture
def recorded_path(tmp_path):
    paths.append(tmp_path)  # ❌ tmp_path cleaned up after test
    return tmp_path

def test_one(recorded_path):
    pass

def test_two():
    # paths[0] no longer exists! ❌
```

## NEVER rely on test execution order

Tests must be independently runnable. pytest does not guarantee execution order (unless explicit with `pytest-order` plugin).

```python
# NEVER — test depends on another test's side effects
def test_create_user():
    # creates user with id=1
    pass

def test_delete_user():
    # ❌ depends on test_create_user having run first
    delete_user(1)
```

```python
# ALWAYS — each test is self-contained
def test_create_and_delete():
    user_id = create_user("alice")
    assert user_id is not None
    result = delete_user(user_id)
    assert result is True
```

## NEVER call `pytest.main()` from within a test file

Calling `pytest.main()` inside a module that pytest is already running causes recursive execution and confusing behavior.

```python
# NEVER
# test_runner.py
import pytest

def test_run_other():
    pytest.main(["test_other.py"])  # ❌ recursive pytest invocation
```

## NEVER ignore the return value of `tmp_path` / `tmp_path_factory`

These fixtures return `pathlib.Path` objects. Treat them as managed resources — don't delete the root directory or rely on specific paths.

```python
# NEVER — deleting tmp_path root breaks the fixture
def test_bad(tmp_path):
    shutil.rmtree(tmp_path)  # ❌ destroys the managed directory
    tmp_path.mkdir()         # may fail

# ALWAYS — work within the directory
def test_good(tmp_path):
    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "file.txt").write_text("data")
    assert (subdir / "file.txt").read_text() == "data"
```
