# pytest — Performance

## Parallel Execution with xdist

```bash
# Run tests across N CPUs
pytest -n auto          # auto-detect CPU count
pytest -n 4             # 4 parallel workers
pytest -n auto --dist loadscope  # group by test module
```

## Slow Test Detection

```bash
# Show slowest tests
pytest --durations=10           # top 10 slowest
pytest --durations=0            # all durations
pytest --durations-min=1.0      # only show tests > 1s
```

## Disable Plugins Not Needed

```bash
# Run without specific plugins
pytest -p no:cacheprovider -p no:doctest
```

## Fixture Scope Tuning

- Use `scope="module"` for DB connections and API clients when tests share them
- Use `scope="session"` for truly immutable setup (config, base URLs)
- Function-scoped fixtures for mutable state — creates overhead but guarantees isolation

## Reducing Test Collection Time

```ini
# pytest.ini — only scan test directories
[pytest]
testpaths = tests
norecursedirs = .git .tox venv env .venv build dist node_modules __pycache__
```

## Test Discovery Caching

```bash
# Cache collected test IDs
pytest --co  # cache write
pytest --co  # subsequent runs use cache
```
