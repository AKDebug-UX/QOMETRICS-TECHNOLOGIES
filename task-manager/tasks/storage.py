"""
tasks/storage.py
────────────────
Handles all JSON file I/O for task persistence.
The task store is a single JSON file: ~/.taskmanager/tasks.json
"""

import json
import os
from pathlib import Path
from typing import List

# Default storage path (overridable via environment variable for tests)
DEFAULT_STORE_PATH = Path.home() / ".taskmanager" / "tasks.json"


def get_store_path() -> Path:
    """
    Return the path to the JSON task store.
    Tests can override this by setting the TASK_STORE_PATH env variable.
    """
    env_path = os.environ.get("TASK_STORE_PATH")
    return Path(env_path) if env_path else DEFAULT_STORE_PATH


def _ensure_store_exists(path: Path) -> None:
    """Create the store file (and its parent directories) if missing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps({"tasks": [], "next_id": 1}, indent=2))


def load_store(path: Path | None = None) -> dict:
    """Read and return the full task store dict."""
    p = path or get_store_path()
    _ensure_store_exists(p)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        # Ensure schema keys exist (forward-compat)
        data.setdefault("tasks", [])
        data.setdefault("next_id", 1)
        return data
    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError(f"Could not read task store at '{p}': {exc}") from exc


def save_store(data: dict, path: Path | None = None) -> None:
    """Write the full task store dict back to disk."""
    p = path or get_store_path()
    _ensure_store_exists(p)
    try:
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Could not write task store at '{p}': {exc}") from exc


def load_tasks(path: Path | None = None) -> List[dict]:
    """Convenience wrapper: return only the tasks list."""
    return load_store(path)["tasks"]
