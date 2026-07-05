"""
tests/conftest.py
─────────────────
Shared pytest fixtures.

Key design: each test function gets its own fresh temporary JSON store,
so tests are completely isolated and never touch the real ~/.taskmanager
directory.
"""

import os
import pytest


@pytest.fixture
def store_path(tmp_path):
    """
    Returns a Path to a temporary task store file.

    Also sets the TASK_STORE_PATH env variable so that manager functions
    that don't receive an explicit `path` argument also use the temp file.
    The env variable is restored after each test.
    """
    p = tmp_path / "tasks.json"
    old = os.environ.get("TASK_STORE_PATH")
    os.environ["TASK_STORE_PATH"] = str(p)
    yield p
    # Restore
    if old is None:
        os.environ.pop("TASK_STORE_PATH", None)
    else:
        os.environ["TASK_STORE_PATH"] = old
