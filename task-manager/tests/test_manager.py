"""
tests/test_manager.py
─────────────────────
Unit tests for tasks/manager.py

Covers:
  add_task      – happy path, edge cases (empty title, invalid priority)
  list_tasks    – all/pending/done filters, priority filter, tag filter
  mark_done     – success, already-done guard, invalid id
  delete_task   – success, invalid id
  edit_task     – title, priority, tags, multi-field, invalid id
  clear_done    – removes only completed tasks
  get_stats     – counts, progress, per-priority breakdown
"""

import pytest
from tasks import manager


# ═══════════════════════════════════════════════════════════════════════════
# add_task
# ═══════════════════════════════════════════════════════════════════════════

class TestAddTask:

    def test_add_returns_task_dict(self, store_path):
        task = manager.add_task("Buy milk", path=store_path)
        assert task["id"]       == 1
        assert task["title"]    == "Buy milk"
        assert task["status"]   == "pending"
        assert task["priority"] == "normal"
        assert task["tags"]     == []
        assert task["created_at"] is not None
        assert task["completed_at"] is None

    def test_add_strips_whitespace(self, store_path):
        task = manager.add_task("  Trim me  ", path=store_path)
        assert task["title"] == "Trim me"

    def test_add_increments_id(self, store_path):
        t1 = manager.add_task("First",  path=store_path)
        t2 = manager.add_task("Second", path=store_path)
        assert t1["id"] == 1
        assert t2["id"] == 2

    def test_add_with_high_priority(self, store_path):
        task = manager.add_task("Urgent!", priority="high", path=store_path)
        assert task["priority"] == "high"

    def test_add_with_tags(self, store_path):
        task = manager.add_task("Tag task", tags=["Work", "Home"], path=store_path)
        assert "work" in task["tags"]
        assert "home" in task["tags"]

    def test_add_ignores_blank_tags(self, store_path):
        task = manager.add_task("Tagged", tags=["  ", "valid", ""], path=store_path)
        assert task["tags"] == ["valid"]

    def test_add_empty_title_raises(self, store_path):
        with pytest.raises(ValueError, match="empty"):
            manager.add_task("", path=store_path)

    def test_add_whitespace_only_title_raises(self, store_path):
        with pytest.raises(ValueError, match="empty"):
            manager.add_task("   ", path=store_path)

    def test_add_invalid_priority_raises(self, store_path):
        with pytest.raises(ValueError, match="Priority"):
            manager.add_task("Task", priority="urgent", path=store_path)

    def test_add_persists_to_disk(self, store_path):
        manager.add_task("Persistent", path=store_path)
        # Load fresh – confirms it was saved
        tasks = manager.list_tasks(path=store_path)
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Persistent"


# ═══════════════════════════════════════════════════════════════════════════
# list_tasks
# ═══════════════════════════════════════════════════════════════════════════

class TestListTasks:

    @pytest.fixture(autouse=True)
    def seed(self, store_path):
        """Seed three tasks: two pending, one done."""
        self.path = store_path
        manager.add_task("Pending A", priority="low",    path=store_path)
        manager.add_task("Pending B", priority="high",   path=store_path)
        t3 = manager.add_task("Done C",    priority="normal", path=store_path)
        manager.mark_done(t3["id"], path=store_path)

    def test_list_all_returns_all(self):
        tasks = manager.list_tasks(path=self.path)
        assert len(tasks) == 3

    def test_list_pending_only(self):
        tasks = manager.list_tasks(status_filter="pending", path=self.path)
        assert all(t["status"] == "pending" for t in tasks)
        assert len(tasks) == 2

    def test_list_done_only(self):
        tasks = manager.list_tasks(status_filter="done", path=self.path)
        assert all(t["status"] == "done" for t in tasks)
        assert len(tasks) == 1

    def test_list_filter_by_priority(self):
        tasks = manager.list_tasks(priority_filter="high", path=self.path)
        assert all(t["priority"] == "high" for t in tasks)
        assert len(tasks) == 1

    def test_list_filter_by_tag(self):
        manager.add_task("Tagged", tags=["important"], path=self.path)
        tasks = manager.list_tasks(tag_filter="important", path=self.path)
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Tagged"

    def test_list_empty_when_no_match(self):
        tasks = manager.list_tasks(tag_filter="nonexistent", path=self.path)
        assert tasks == []

    def test_list_invalid_status_filter_raises(self):
        with pytest.raises(ValueError):
            manager.list_tasks(status_filter="invalid", path=self.path)

    def test_list_invalid_priority_filter_raises(self):
        with pytest.raises(ValueError):
            manager.list_tasks(priority_filter="critical", path=self.path)


# ═══════════════════════════════════════════════════════════════════════════
# mark_done
# ═══════════════════════════════════════════════════════════════════════════

class TestMarkDone:

    def test_mark_done_sets_status(self, store_path):
        t = manager.add_task("Task", path=store_path)
        updated = manager.mark_done(t["id"], path=store_path)
        assert updated["status"]       == "done"
        assert updated["completed_at"] is not None

    def test_mark_done_persists(self, store_path):
        t = manager.add_task("Task", path=store_path)
        manager.mark_done(t["id"], path=store_path)
        tasks = manager.list_tasks(status_filter="done", path=store_path)
        assert len(tasks) == 1

    def test_mark_done_invalid_id_raises(self, store_path):
        with pytest.raises(KeyError, match="999"):
            manager.mark_done(999, path=store_path)

    def test_mark_done_already_done_raises(self, store_path):
        t = manager.add_task("Task", path=store_path)
        manager.mark_done(t["id"], path=store_path)
        with pytest.raises(ValueError, match="already"):
            manager.mark_done(t["id"], path=store_path)

    def test_mark_done_returns_task(self, store_path):
        t = manager.add_task("Return me", path=store_path)
        result = manager.mark_done(t["id"], path=store_path)
        assert result["id"]    == t["id"]
        assert result["title"] == "Return me"


# ═══════════════════════════════════════════════════════════════════════════
# delete_task
# ═══════════════════════════════════════════════════════════════════════════

class TestDeleteTask:

    def test_delete_removes_task(self, store_path):
        t = manager.add_task("Delete me", path=store_path)
        manager.delete_task(t["id"], path=store_path)
        tasks = manager.list_tasks(path=store_path)
        assert not any(tk["id"] == t["id"] for tk in tasks)

    def test_delete_returns_deleted_task(self, store_path):
        t = manager.add_task("Return after delete", path=store_path)
        deleted = manager.delete_task(t["id"], path=store_path)
        assert deleted["id"]    == t["id"]
        assert deleted["title"] == "Return after delete"

    def test_delete_invalid_id_raises(self, store_path):
        with pytest.raises(KeyError, match="42"):
            manager.delete_task(42, path=store_path)

    def test_delete_leaves_other_tasks(self, store_path):
        t1 = manager.add_task("Keep me",   path=store_path)
        t2 = manager.add_task("Delete me", path=store_path)
        manager.delete_task(t2["id"], path=store_path)
        remaining = manager.list_tasks(path=store_path)
        assert len(remaining) == 1
        assert remaining[0]["id"] == t1["id"]

    def test_delete_completed_task(self, store_path):
        t = manager.add_task("Done task", path=store_path)
        manager.mark_done(t["id"], path=store_path)
        manager.delete_task(t["id"], path=store_path)
        assert manager.list_tasks(path=store_path) == []


# ═══════════════════════════════════════════════════════════════════════════
# edit_task
# ═══════════════════════════════════════════════════════════════════════════

class TestEditTask:

    def test_edit_title(self, store_path):
        t = manager.add_task("Old title", path=store_path)
        updated = manager.edit_task(t["id"], title="New title", path=store_path)
        assert updated["title"] == "New title"

    def test_edit_priority(self, store_path):
        t = manager.add_task("Task", priority="low", path=store_path)
        updated = manager.edit_task(t["id"], priority="high", path=store_path)
        assert updated["priority"] == "high"

    def test_edit_tags(self, store_path):
        t = manager.add_task("Task", tags=["old"], path=store_path)
        updated = manager.edit_task(t["id"], tags=["new1", "new2"], path=store_path)
        assert updated["tags"] == ["new1", "new2"]

    def test_edit_multiple_fields(self, store_path):
        t = manager.add_task("Task", path=store_path)
        updated = manager.edit_task(t["id"], title="Multi", priority="high", path=store_path)
        assert updated["title"]    == "Multi"
        assert updated["priority"] == "high"

    def test_edit_invalid_id_raises(self, store_path):
        with pytest.raises(KeyError):
            manager.edit_task(99, title="X", path=store_path)

    def test_edit_empty_title_raises(self, store_path):
        t = manager.add_task("Valid", path=store_path)
        with pytest.raises(ValueError, match="empty"):
            manager.edit_task(t["id"], title="  ", path=store_path)

    def test_edit_invalid_priority_raises(self, store_path):
        t = manager.add_task("Task", path=store_path)
        with pytest.raises(ValueError, match="Priority"):
            manager.edit_task(t["id"], priority="critical", path=store_path)

    def test_edit_persists(self, store_path):
        t = manager.add_task("Old", path=store_path)
        manager.edit_task(t["id"], title="Saved", path=store_path)
        reloaded = manager.list_tasks(path=store_path)[0]
        assert reloaded["title"] == "Saved"


# ═══════════════════════════════════════════════════════════════════════════
# clear_done
# ═══════════════════════════════════════════════════════════════════════════

class TestClearDone:

    def test_clear_removes_completed(self, store_path):
        t1 = manager.add_task("Pending",   path=store_path)
        t2 = manager.add_task("Completed", path=store_path)
        manager.mark_done(t2["id"], path=store_path)
        removed = manager.clear_done(path=store_path)
        assert removed == 1
        remaining = manager.list_tasks(path=store_path)
        assert len(remaining) == 1
        assert remaining[0]["id"] == t1["id"]

    def test_clear_empty_returns_zero(self, store_path):
        assert manager.clear_done(path=store_path) == 0

    def test_clear_all_done(self, store_path):
        for i in range(3):
            t = manager.add_task(f"Task {i}", path=store_path)
            manager.mark_done(t["id"], path=store_path)
        removed = manager.clear_done(path=store_path)
        assert removed == 3
        assert manager.list_tasks(path=store_path) == []

    def test_clear_no_pending_affected(self, store_path):
        manager.add_task("Pending A", path=store_path)
        manager.add_task("Pending B", path=store_path)
        removed = manager.clear_done(path=store_path)
        assert removed == 0
        assert len(manager.list_tasks(path=store_path)) == 2


# ═══════════════════════════════════════════════════════════════════════════
# get_stats
# ═══════════════════════════════════════════════════════════════════════════

class TestGetStats:

    def test_stats_empty_store(self, store_path):
        stats = manager.get_stats(path=store_path)
        assert stats["total"]   == 0
        assert stats["done"]    == 0
        assert stats["pending"] == 0

    def test_stats_counts(self, store_path):
        t1 = manager.add_task("A", priority="high",   path=store_path)
        t2 = manager.add_task("B", priority="low",    path=store_path)
        _  = manager.add_task("C", priority="normal", path=store_path)
        manager.mark_done(t1["id"], path=store_path)
        manager.mark_done(t2["id"], path=store_path)

        stats = manager.get_stats(path=store_path)
        assert stats["total"]   == 3
        assert stats["done"]    == 2
        assert stats["pending"] == 1

    def test_stats_by_priority(self, store_path):
        manager.add_task("L", priority="low",    path=store_path)
        manager.add_task("L", priority="low",    path=store_path)
        manager.add_task("H", priority="high",   path=store_path)

        stats = manager.get_stats(path=store_path)
        assert stats["by_priority"]["low"]    == 2
        assert stats["by_priority"]["high"]   == 1
        assert stats["by_priority"]["normal"] == 0
