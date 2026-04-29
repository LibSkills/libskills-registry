# pytest — Overview

**pytest** is a mature, full-featured Python testing framework. It makes writing simple tests easy and scales to support complex functional testing for applications and libraries.

## When to Use

- Unit testing, integration testing, and functional testing in Python
- Replacing `unittest` with less boilerplate and more expressive assertions
- Testing data pipelines, web applications, CLI tools, and API services
- Parameterized testing with concise, readable test definitions

## When NOT to Use

- Performance/stress testing (use `locust`, `k6`, or `vegeta` for load testing)
- Formal property-based testing (use `hypothesis` with pytest as the runner)
- Browser-level end-to-end testing without a companion like `selenium` or `playwright`

## Key Design

- **Auto-discovery**: pytest finds `test_*.py` / `*_test.py` files and `test_*` functions/methods recursively
- **Fixtures**: pytest's dependency injection system for setup/teardown, shared through `conftest.py`
- **Assertions**: Uses plain `assert` with rich failure introspection (no need for `self.assertEqual(...)`)
- **Plugins**: Rich plugin ecosystem — `pytest-cov` (coverage), `pytest-xdist` (parallel), `pytest-mock` (mocking), `pytest-asyncio` (async tests)
- **Marks**: Built-in markers for skipping (`@pytest.mark.skip`), expecting failure (`@pytest.mark.xfail`), and custom categorization (`@pytest.mark.slow`)
- **Parametrization**: Run the same test with multiple inputs using `@pytest.mark.parametrize`
- **Fixture scopes**: `function` (default), `class`, `module`, `package`, `session` — control fixture lifespan
