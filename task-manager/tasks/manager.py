"""
tasks/manager.py
────────────────
CRUD operations for tasks. All functions are pure Python and testable
in isolation – they accept an optional `path` argument so tests can
redirect I/O to a temporary file without touching real storage.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from tasks.storage import load_store, save_store

# Valid priority levels (ordered)
PRIORITIES   = ("low", "normal", "high")
VALID_STATUS = ("pending", "done")


# ── Internal helpers ──────────────────────────────────────────────────────

def _now_iso() -> str:
    """Return current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _find_task(tasks: List[dict], task_id: int) -> Optional[dict]:
    """Return the task with the given id, or None if not found."""
    return next((t for t in tasks if t["id"] == task_id), None)


# ── CRUD operations ───────────────────────────────────────────────────────

def add_task(
    title: str,
    priority: str = "normal",
    tags: Optional[List[str]] = None,
    path: Optional[Path] = None,
) -> dict:
    """
    Create a new task and persist it.

    Parameters
    ----------
    title    : Task description (must be non-empty after stripping).
    priority : One of 'low', 'normal', 'high'.
    tags     : Optional list of tag strings.
    path     : Override storage path (for tests).

    Returns
    -------
    The newly created task dict.

    Raises
    ------
    ValueError if title is blank or priority is invalid.
    """
    title = title.strip()
    if not title:
        raise ValueError("Task title cannot be empty.")
    if priority not in PRIORITIES:
        raise ValueError(f"Priority must be one of {PRIORITIES}. Got '{priority}'.")

    store = load_store(path)
    task = {
        "id":           store["next_id"],
        "title":        title,
        "priority":     priority,
        "tags":         [t.strip().lower() for t in (tags or []) if t.strip()],
        "status":       "pending",
        "created_at":   _now_iso(),
        "completed_at": None,
    }
    store["tasks"].append(task)
    store["next_id"] += 1
    save_store(store, path)
    return task


def list_tasks(
    status_filter: str = "all",
    priority_filter: Optional[str] = None,
    tag_filter: Optional[str] = None,
    path: Optional[Path] = None,
) -> List[dict]:
    """
    Return tasks, optionally filtered.

    Parameters
    ----------
    status_filter   : 'all', 'pending', or 'done'.
    priority_filter : Optional priority to restrict to.
    tag_filter      : Optional tag string to restrict to.
    path            : Override storage path (for tests).
    """
    if status_filter not in ("all", *VALID_STATUS):
        raise ValueError(f"status_filter must be one of: all, pending, done.")

    tasks = load_store(path)["tasks"]

    if status_filter != "all":
        tasks = [t for t in tasks if t["status"] == status_filter]
    if priority_filter:
        if priority_filter not in PRIORITIES:
            raise ValueError(f"Priority must be one of {PRIORITIES}.")
        tasks = [t for t in tasks if t["priority"] == priority_filter]
    if tag_filter:
        tag_lower = tag_filter.strip().lower()
        tasks = [t for t in tasks if tag_lower in t.get("tags", [])]

    return tasks


def mark_done(task_id: int, path: Optional[Path] = None) -> dict:
    """
    Mark a task as completed.

    Returns the updated task.

    Raises
    ------
    KeyError  if no task with that id exists.
    ValueError if the task is already done.
    """
    store = load_store(path)
    task  = _find_task(store["tasks"], task_id)

    if task is None:
        raise KeyError(f"No task found with id {task_id}.")
    if task["status"] == "done":
        raise ValueError(f"Task {task_id} is already marked as done.")

    task["status"]       = "done"
    task["completed_at"] = _now_iso()
    save_store(store, path)
    return task


def delete_task(task_id: int, path: Optional[Path] = None) -> dict:
    """
    Permanently remove a task.

    Returns the deleted task.

    Raises
    ------
    KeyError if no task with that id exists.
    """
    store = load_store(path)
    task  = _find_task(store["tasks"], task_id)

    if task is None:
        raise KeyError(f"No task found with id {task_id}.")

    store["tasks"] = [t for t in store["tasks"] if t["id"] != task_id]
    save_store(store, path)
    return task


def edit_task(
    task_id:          int,
    title:            Optional[str]       = None,
    priority:         Optional[str]       = None,
    tags:             Optional[List[str]] = None,
    path:             Optional[Path]      = None,
) -> dict:
    """
    Update an existing task's fields.

    Only the provided (non-None) fields are modified.

    Returns the updated task.
    """
    store = load_store(path)
    task  = _find_task(store["tasks"], task_id)

    if task is None:
        raise KeyError(f"No task found with id {task_id}.")

    if title is not None:
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty.")
        task["title"] = title

    if priority is not None:
        if priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of {PRIORITIES}.")
        task["priority"] = priority

    if tags is not None:
        task["tags"] = [t.strip().lower() for t in tags if t.strip()]

    save_store(store, path)
    return task


def clear_done(path: Optional[Path] = None) -> int:
    """
    Remove all completed tasks.

    Returns the number of tasks removed.
    """
    store    = load_store(path)
    original = len(store["tasks"])
    store["tasks"] = [t for t in store["tasks"] if t["status"] != "done"]
    removed  = original - len(store["tasks"])
    save_store(store, path)
    return removed


def get_stats(path: Optional[Path] = None) -> dict:
    """Return a summary dict with task counts."""
    tasks   = load_store(path)["tasks"]
    total   = len(tasks)
    done    = sum(1 for t in tasks if t["status"] == "done")
    pending = total - done
    by_priority = {p: sum(1 for t in tasks if t["priority"] == p) for p in PRIORITIES}
    return {
        "total":       total,
        "done":        done,
        "pending":     pending,
        "by_priority": by_priority,
    }
