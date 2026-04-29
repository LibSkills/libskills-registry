"""Example pytest test suite demonstrating core features."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest


# --- Domain logic to test ---

@dataclass
class User:
    id: Optional[int] = None
    name: str = ""
    email: str = ""

    def validate(self) -> bool:
        return bool(self.name) and "@" in self.email

    @property
    def display_name(self) -> str:
        return self.name.title()


class UserRepository:
    """Simulates a user repository backed by JSON in a temp file."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        if not db_path.exists():
            self._save([])

    def _load(self) -> list:
        return json.loads(self.db_path.read_text())

    def _save(self, users: list) -> None:
        self.db_path.write_text(json.dumps(users))

    def add(self, user: User) -> User:
        users = self._load()
        user.id = len(users) + 1
        users.append({"id": user.id, "name": user.name, "email": user.email})
        self._save(users)
        return user

    def get(self, user_id: int) -> Optional[User]:
        for u in self._load():
            if u["id"] == user_id:
                return User(**u)
        return None

    def list_all(self) -> list[User]:
        return [User(**u) for u in self._load()]

    def count(self) -> int:
        return len(self._load())


# --- Fixtures ---

@pytest.fixture
def repo(tmp_path: Path) -> UserRepository:
    """Create a fresh UserRepository for each test."""
    return UserRepository(tmp_path / "users.json")


@pytest.fixture
def alice() -> User:
    return User(name="alice", email="alice@example.com")


@pytest.fixture
def bob() -> User:
    return User(name="bob", email="bob@example.com")


# --- Tests ---

class TestUser:
    """Tests for the User dataclass."""

    def test_valid_user(self):
        user = User(name="alice", email="alice@example.com")
        assert user.validate() is True

    def test_invalid_user_no_name(self):
        user = User(email="alice@example.com")
        assert user.validate() is False

    def test_invalid_user_bad_email(self):
        user = User(name="alice", email="not-an-email")
        assert user.validate() is False

    def test_display_name(self):
        user = User(name="alice smith")
        assert user.display_name == "Alice Smith"

    @pytest.mark.parametrize("name,email,expected", [
        ("alice", "alice@example.com", True),
        ("", "alice@example.com", False),
        ("alice", "invalid", False),
        ("", "", False),
    ])
    def test_validate_parametrized(self, name: str, email: str, expected: bool):
        user = User(name=name, email=email)
        assert user.validate() == expected


class TestUserRepository:
    """Tests for UserRepository using fixture-based DB."""

    def test_add_user(self, repo: UserRepository, alice: User):
        saved = repo.add(alice)
        assert saved.id == 1
        assert repo.count() == 1

    def test_add_multiple_users(self, repo: UserRepository, alice: User, bob: User):
        repo.add(alice)
        repo.add(bob)
        assert repo.count() == 2

    def test_get_user(self, repo: UserRepository, alice: User):
        saved = repo.add(alice)
        fetched = repo.get(saved.id)
        assert fetched is not None
        assert fetched.name == "alice"
        assert fetched.email == "alice@example.com"

    def test_get_nonexistent_user(self, repo: UserRepository):
        assert repo.get(999) is None

    def test_list_users_empty(self, repo: UserRepository):
        assert repo.list_all() == []

    def test_list_users(self, repo: UserRepository, alice: User, bob: User):
        repo.add(alice)
        repo.add(bob)
        users = repo.list_all()
        assert len(users) == 2

    def test_repository_isolation(self, repo: UserRepository):
        """Each test gets a fresh repo — no state leakage."""
        assert repo.count() == 0  # no leftover from previous tests


class TestConftestIntegration:
    """Tests using fixtures from conftest.py (if available)."""

    def test_tmp_path_exists(self, tmp_path: Path):
        """tmp_path is a built-in pytest fixture."""
        assert tmp_path.exists()
        assert tmp_path.is_dir()

    def test_tmp_path_writes(self, tmp_path: Path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello pytest")
        assert test_file.read_text() == "hello pytest"

    def test_monkeypatch_env(self, monkeypatch):
        monkeypatch.setenv("APP_ENV", "testing")
        assert os.environ["APP_ENV"] == "testing"

    def test_monkeypatch_restores(self, monkeypatch):
        """Original env value restored after test."""
        monkeypatch.setenv("TEST_VAR", "temp")
        assert os.environ["TEST_VAR"] == "temp"
        # After test, TEST_VAR is removed (not present originally)

    def test_raises_exception(self):
        with pytest.raises(ValueError, match="invalid"):
            raise ValueError("invalid input")

    def test_approx_floats(self):
        assert 0.1 + 0.2 == pytest.approx(0.3)
        assert 100.0 == pytest.approx(100.1, rel=1e-2)

    @pytest.mark.skip(reason="not implemented yet")
    def test_skipped(self):
        assert False  # won't run


class TestMarkers:
    """Demonstrating pytest markers."""

    @pytest.mark.slow
    def test_slow_operation(self):
        """Use: pytest -m slow to run only slow tests."""
        result = sum(range(1_000_000))
        assert result > 0

    @pytest.mark.xfail(reason="known issue #42")
    def test_expected_failure(self):
        """Expected to fail. If it passes, pytest reports XPASS."""
        assert 1 == 2  # currently fails as expected
