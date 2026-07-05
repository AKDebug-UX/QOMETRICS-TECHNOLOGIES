"""
tests/test_storage.py
─────────────────────
Unit tests for tasks/storage.py

Covers:
  load_store  – creates file if missing, parses valid JSON, handles corruption
  save_store  – writes to disk, round-trips correctly
  load_tasks  – returns tasks list only
"""

import json
import pytest
from tasks.storage import load_store, save_store, load_tasks


class TestLoadStore:

    def test_creates_file_when_missing(self, store_path):
        assert not store_path.exists()
        data = load_store(store_path)
        assert store_path.exists()
        assert data["tasks"]   == []
        assert data["next_id"] == 1

    def test_reads_existing_data(self, store_path):
        payload = {"tasks": [{"id": 1, "title": "Saved"}], "next_id": 2}
        store_path.write_text(json.dumps(payload))
        data = load_store(store_path)
        assert data["tasks"][0]["title"] == "Saved"
        assert data["next_id"] == 2

    def test_defaults_missing_keys(self, store_path):
        """If the JSON file exists but lacks schema keys, defaults are applied."""
        store_path.parent.mkdir(parents=True, exist_ok=True)
        store_path.write_text("{}")
        data = load_store(store_path)
        assert "tasks"   in data
        assert "next_id" in data

    def test_corrupted_json_raises(self, store_path):
        store_path.parent.mkdir(parents=True, exist_ok=True)
        store_path.write_text("NOT VALID JSON!!!")
        with pytest.raises(RuntimeError, match="Could not read"):
            load_store(store_path)

    def test_creates_parent_directories(self, tmp_path):
        deep = tmp_path / "a" / "b" / "c" / "tasks.json"
        assert not deep.parent.exists()
        load_store(deep)
        assert deep.exists()


class TestSaveStore:

    def test_save_creates_file(self, store_path):
        save_store({"tasks": [], "next_id": 1}, store_path)
        assert store_path.exists()

    def test_round_trip(self, store_path):
        original = {"tasks": [{"id": 1, "title": "Hello"}], "next_id": 2}
        save_store(original, store_path)
        loaded = load_store(store_path)
        assert loaded["tasks"][0]["title"] == "Hello"
        assert loaded["next_id"] == 2

    def test_save_unicode(self, store_path):
        payload = {"tasks": [{"title": "日本語テスト"}], "next_id": 2}
        save_store(payload, store_path)
        loaded = load_store(store_path)
        assert loaded["tasks"][0]["title"] == "日本語テスト"

    def test_save_overwrites_existing(self, store_path):
        save_store({"tasks": [{"id": 1}], "next_id": 2}, store_path)
        save_store({"tasks": [],           "next_id": 1}, store_path)
        loaded = load_store(store_path)
        assert loaded["tasks"] == []


class TestLoadTasks:

    def test_returns_list(self, store_path):
        result = load_tasks(store_path)
        assert isinstance(result, list)

    def test_returns_tasks_subset(self, store_path):
        payload = {"tasks": [{"id": 1}, {"id": 2}], "next_id": 3}
        store_path.parent.mkdir(parents=True, exist_ok=True)
        store_path.write_text(json.dumps(payload))
        tasks = load_tasks(store_path)
        assert len(tasks) == 2

    def test_empty_store_returns_empty_list(self, store_path):
        assert load_tasks(store_path) == []
