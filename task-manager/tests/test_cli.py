"""
tests/test_cli.py
─────────────────
Integration tests for the CLI argument parsing (main.py).

We call main(argv=[...]) directly so tests run without subprocess overhead.
All output to stdout is captured by pytest's capsys.
"""

import pytest
from unittest.mock import patch
from main import main


# ── Helpers ───────────────────────────────────────────────────────────────

def run(*args, store_path):
    """Run main() with the given args against a temp store."""
    with patch.dict("os.environ", {"TASK_STORE_PATH": str(store_path)}):
        return main(list(args))


# ── add ───────────────────────────────────────────────────────────────────

class TestCLIAdd:

    def test_add_exit_zero(self, store_path):
        assert run("add", "Buy milk", store_path=store_path) == 0

    def test_add_invalid_priority_exits_nonzero(self, store_path, capsys):
        code = run("add", "Task", "--priority", "urgent", store_path=store_path)
        assert code != 0

    def test_add_empty_title_exits_nonzero(self, store_path):
        code = run("add", "   ", store_path=store_path)
        assert code != 0

    def test_add_with_tags_exit_zero(self, store_path):
        code = run("add", "Tagged task", "--tags", "work", "home", store_path=store_path)
        assert code == 0


# ── list ──────────────────────────────────────────────────────────────────

class TestCLIList:

    def test_list_empty_exit_zero(self, store_path):
        assert run("list", store_path=store_path) == 0

    def test_list_with_filter_exit_zero(self, store_path):
        run("add", "A task", store_path=store_path)
        assert run("list", "--filter", "pending", store_path=store_path) == 0

    def test_list_with_priority_filter_exit_zero(self, store_path):
        run("add", "Task", "--priority", "high", store_path=store_path)
        assert run("list", "--priority", "high", store_path=store_path) == 0


# ── done ─────────────────────────────────────────────────────────────────

class TestCLIDone:

    def test_done_exit_zero(self, store_path):
        run("add", "Task", store_path=store_path)
        assert run("done", "1", store_path=store_path) == 0

    def test_done_invalid_id_exits_nonzero(self, store_path, capsys):
        code = run("done", "999", store_path=store_path)
        assert code != 0

    def test_done_already_done_exit_zero(self, store_path):
        """Already-done is a warning, not an error – returns 0."""
        run("add", "Task", store_path=store_path)
        run("done", "1", store_path=store_path)
        assert run("done", "1", store_path=store_path) == 0


# ── delete ────────────────────────────────────────────────────────────────

class TestCLIDelete:

    def test_delete_exit_zero(self, store_path):
        run("add", "Delete me", store_path=store_path)
        assert run("delete", "1", store_path=store_path) == 0

    def test_delete_invalid_id_exits_nonzero(self, store_path):
        code = run("delete", "999", store_path=store_path)
        assert code != 0

    def test_rm_alias_works(self, store_path):
        run("add", "Task", store_path=store_path)
        assert run("rm", "1", store_path=store_path) == 0


# ── edit ─────────────────────────────────────────────────────────────────

class TestCLIEdit:

    def test_edit_title_exit_zero(self, store_path):
        run("add", "Old", store_path=store_path)
        assert run("edit", "1", "--title", "New", store_path=store_path) == 0

    def test_edit_no_fields_exits_nonzero(self, store_path, capsys):
        run("add", "Task", store_path=store_path)
        code = run("edit", "1", store_path=store_path)
        assert code != 0

    def test_edit_invalid_id_exits_nonzero(self, store_path):
        code = run("edit", "999", "--title", "X", store_path=store_path)
        assert code != 0


# ── clear ────────────────────────────────────────────────────────────────

class TestCLIClear:

    def test_clear_exit_zero(self, store_path):
        assert run("clear", store_path=store_path) == 0

    def test_clear_removes_done_tasks(self, store_path):
        run("add",  "A",   store_path=store_path)
        run("done", "1",   store_path=store_path)
        run("clear",       store_path=store_path)
        # After clearing, list should be empty
        from tasks import manager
        import os
        with patch.dict("os.environ", {"TASK_STORE_PATH": str(store_path)}):
            tasks = manager.list_tasks(path=store_path)
        assert tasks == []


# ── stats ─────────────────────────────────────────────────────────────────

class TestCLIStats:

    def test_stats_exit_zero(self, store_path):
        assert run("stats", store_path=store_path) == 0

    def test_stats_output_contains_counts(self, store_path, capsys):
        run("add", "Task A", store_path=store_path)
        run("stats", store_path=store_path)
        out = capsys.readouterr().out
        # Stats should mention something about tasks
        assert "0" in out or "1" in out
