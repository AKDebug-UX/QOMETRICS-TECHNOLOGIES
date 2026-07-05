# ⚡ Task Manager CLI – Qometrics Technologies

A feature-rich command-line task manager built with Python. Manage tasks directly from your terminal with colourful output, persistent storage, and full test coverage.

## Features

| Feature | Detail |
|---|---|
| 📋 CRUD | add, list, done, delete, edit |
| 🎨 Colours | Colorama-powered priority/status highlighting |
| 💾 Persistence | JSON file in `~/.taskmanager/tasks.json` |
| 🏷️ Tags | Attach searchable tags to tasks |
| 🔺 Priorities | low / normal / high with colour coding |
| 📊 Stats | Progress bar, counts by status & priority |
| 🧪 Tests | 44+ pytest tests across 3 test modules |

## Project Structure

```
task-manager/
├── main.py                ← CLI entry point (argparse)
├── tasks/
│   ├── __init__.py
│   ├── manager.py         ← CRUD operations
│   ├── storage.py         ← JSON file I/O
│   └── display.py         ← Colorama output helpers
├── tests/
│   ├── conftest.py        ← Shared fixtures (isolated temp store)
│   ├── test_manager.py    ← 30+ unit tests for CRUD
│   ├── test_storage.py    ← Storage I/O tests
│   └── test_cli.py        ← CLI integration tests
├── pyproject.toml         ← Pytest + coverage config
└── requirements.txt
```

## Installation

```bash
cd "e:\QOMETRICS TECHNOLOGIES\task-manager"

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Add tasks
python main.py add "Buy groceries" --priority high --tags shopping food
python main.py add "Write unit tests" --priority normal --tags work

# List tasks
python main.py list                          # all tasks
python main.py list --filter pending         # only pending
python main.py list --filter done            # only completed
python main.py list --priority high          # filter by priority
python main.py list --tag work               # filter by tag

# Complete a task
python main.py done 1

# Delete a task
python main.py delete 2
python main.py rm 2      # alias

# Edit a task
python main.py edit 3 --title "Updated title"
python main.py edit 3 --priority low --tags home errands

# Clear all completed tasks
python main.py clear

# Show statistics
python main.py stats
```

## Optional: Add to PATH

Create a `task.bat` in your PATH for even shorter commands:

```bat
@echo off
python "e:\QOMETRICS TECHNOLOGIES\task-manager\main.py" %*
```

Then use:
```
task add "Buy milk" --priority high
task list --filter pending
task done 1
```

## Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=tasks --cov-report=term-missing

# Run specific test file
pytest tests/test_manager.py -v
```

## Task JSON Schema

Each task is stored as:

```json
{
  "id": 1,
  "title": "Buy groceries",
  "priority": "high",
  "tags": ["shopping", "food"],
  "status": "pending",
  "created_at": "2026-07-05T10:00:00",
  "completed_at": null
}
```

## Output Preview

```
  ╔══════════════════════════════╗
  ║  ⚡  Task Manager CLI  v1.0  ║
  ╚══════════════════════════════╝

  ──────────────────────────────────────────────────────────────────────────
  All Tasks  (3 items)
  ──────────────────────────────────────────────────────────────────────────
  ID  ○  Title                              Priority          Date
  ──────────────────────────────────────────────────────────────────────────
    1  ○  Buy groceries  #shopping #food   [▲ HIGH]          2026-07-05
    2  ○  Write unit tests  #work          [◇ NORMAL]        2026-07-05
    3  ✓  Setup project                    [▽ LOW]           2026-07-05
  ──────────────────────────────────────────────────────────────────────────
```
