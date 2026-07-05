from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from tasks.storage import load_store, save_store

PRIORITIES = ("low", "normal", "high")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _find(tasks, task_id):
    return next((t for t in tasks if t["id"] == task_id), None)


def add_task(title: str, priority="normal", tags=None, path=None) -> dict:
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
        "created_at":   _now(),
        "completed_at": None,
    }
    store["tasks"].append(task)
    store["next_id"] += 1
    save_store(store, path)
    return task


def list_tasks(status_filter="all", priority_filter=None, tag_filter=None, path=None):
    if status_filter not in ("all", "pending", "done"):
        raise ValueError("status_filter must be one of: all, pending, done.")

    tasks = load_store(path)["tasks"]

    if status_filter != "all":
        tasks = [t for t in tasks if t["status"] == status_filter]
    if priority_filter:
        if priority_filter not in PRIORITIES:
            raise ValueError(f"Priority must be one of {PRIORITIES}.")
        tasks = [t for t in tasks if t["priority"] == priority_filter]
    if tag_filter:
        tag = tag_filter.strip().lower()
        tasks = [t for t in tasks if tag in t.get("tags", [])]

    return tasks


def mark_done(task_id: int, path=None) -> dict:
    store = load_store(path)
    task = _find(store["tasks"], task_id)

    if task is None:
        raise KeyError(f"No task found with id {task_id}.")
    if task["status"] == "done":
        raise ValueError(f"Task {task_id} is already marked as done.")

    task["status"] = "done"
    task["completed_at"] = _now()
    save_store(store, path)
    return task


def delete_task(task_id: int, path=None) -> dict:
    store = load_store(path)
    task = _find(store["tasks"], task_id)

    if task is None:
        raise KeyError(f"No task found with id {task_id}.")

    store["tasks"] = [t for t in store["tasks"] if t["id"] != task_id]
    save_store(store, path)
    return task


def edit_task(task_id: int, title=None, priority=None, tags=None, path=None) -> dict:
    store = load_store(path)
    task = _find(store["tasks"], task_id)

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


def clear_done(path=None) -> int:
    store = load_store(path)
    before = len(store["tasks"])
    store["tasks"] = [t for t in store["tasks"] if t["status"] != "done"]
    save_store(store, path)
    return before - len(store["tasks"])


def get_stats(path=None) -> dict:
    tasks = load_store(path)["tasks"]
    done = sum(1 for t in tasks if t["status"] == "done")
    return {
        "total":       len(tasks),
        "done":        done,
        "pending":     len(tasks) - done,
        "by_priority": {p: sum(1 for t in tasks if t["priority"] == p) for p in PRIORITIES},
    }
