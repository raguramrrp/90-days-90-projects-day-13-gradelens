"""
GradeLens Pytest Configuration & Test Database Fixtures.
Provides isolated, clean in-memory or temporary database instances for test execution.
"""

import pytest
import tempfile
from pathlib import Path
from src.database.connection import DatabaseManager
from src.database.schema import init_database
from src.database.repository import Repository
from src.data.seeder import seed_database


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """Creates a temporary SQLite file for the test session."""
    tmp_dir = tmp_path_factory.mktemp("gradelens_test")
    return tmp_dir / "test_gradelens.db"


@pytest.fixture(scope="session")
def test_db_manager(test_db_path):
    """Initializes and seeds an isolated test database manager."""
    mgr = DatabaseManager(override_type="sqlite", sqlite_path=str(test_db_path))
    init_database(mgr)
    seed_database(mgr, force_reset=True)
    return mgr


@pytest.fixture(scope="session")
def test_repo(test_db_manager):
    """Returns a repository instance pointing to the test database."""
    return Repository(manager=test_db_manager)
