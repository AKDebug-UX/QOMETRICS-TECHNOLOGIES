import json
import os
from pathlib import Path
from typing import List

DEFAULT_STORE = Path.home() / ".taskmanager" / "tasks.json"


def get_store_path() -> Path:
    p = os.environ.get("TASK_STORE_PATH")
    return Path(p) if p else DEFAULT_STORE


def _init_file(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps({"tasks": [], "next_id": 1}, indent=2))


def load_store(path: Path = None) -> dict:
    p = path or get_store_path()
    _init_file(p)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        data.setdefault("tasks", [])
        data.setdefault("next_id", 1)
        return data
    except (json.JSONDecodeError, OSError) as e:
        raise RuntimeError(f"Could not read task store at '{p}': {e}") from e


def save_store(data: dict, path: Path = None):
    p = path or get_store_path()
    _init_file(p)
    try:
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as e:
        raise RuntimeError(f"Could not write to '{p}': {e}") from e


def load_tasks(path: Path = None) -> List[dict]:
    return load_store(path)["tasks"]

