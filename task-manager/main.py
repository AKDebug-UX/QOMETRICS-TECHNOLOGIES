#!/usr/bin/env python3
"""
main.py  –  Task Manager CLI
─────────────────────────────
Entry point. Parses arguments and dispatches to the appropriate
manager function, then formats output via the display module.

Usage examples
──────────────
  python main.py add "Buy groceries" --priority high --tags shopping food
  python main.py list
  python main.py list --filter pending --priority high
  python main.py done 3
  python main.py delete 5
  python main.py edit 2 --title "Updated title" --priority low
  python main.py clear
  python main.py stats
"""

import argparse
import sys

from tasks import display as ui
from tasks import manager


# ── Sub-command handlers ─────────────────────────────────────────────────

def cmd_add(args: argparse.Namespace) -> int:
    """Handle: python main.py add <title> [options]"""
    try:
        task = manager.add_task(
            title    = args.title,
            priority = args.priority,
            tags     = args.tags or [],
        )
        ui.print_success(
            f"Task #{task['id']} added: \"{task['title']}\""
            f"  [{task['priority'].upper()}]"
        )
        return 0
    except ValueError as exc:
        ui.print_error(str(exc))
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """Handle: python main.py list [options]"""
    try:
        tasks = manager.list_tasks(
            status_filter   = args.filter,
            priority_filter = args.priority,
            tag_filter      = args.tag,
        )
        label_map = {
            "all":     "All Tasks",
            "pending": "Pending Tasks",
            "done":    "Completed Tasks",
        }
        ui.print_task_list(tasks, title=label_map.get(args.filter, "Tasks"))
        return 0
    except ValueError as exc:
        ui.print_error(str(exc))
        return 1


def cmd_done(args: argparse.Namespace) -> int:
    """Handle: python main.py done <id>"""
    try:
        task = manager.mark_done(args.id)
        ui.print_success(f"Task #{task['id']} marked as done: \"{task['title']}\"")
        return 0
    except KeyError as exc:
        ui.print_error(str(exc))
        return 1
    except ValueError as exc:
        ui.print_warning(str(exc))
        return 0


def cmd_delete(args: argparse.Namespace) -> int:
    """Handle: python main.py delete <id>"""
    try:
        task = manager.delete_task(args.id)
        ui.print_success(f"Task #{task['id']} deleted: \"{task['title']}\"")
        return 0
    except KeyError as exc:
        ui.print_error(str(exc))
        return 1


def cmd_edit(args: argparse.Namespace) -> int:
    """Handle: python main.py edit <id> [options]"""
    # At least one field must be changed
    if args.title is None and args.priority is None and args.tags is None:
        ui.print_error("Specify at least one field to edit: --title, --priority, --tags")
        return 1
    try:
        task = manager.edit_task(
            task_id  = args.id,
            title    = args.title,
            priority = args.priority,
            tags     = args.tags,
        )
        ui.print_success(f"Task #{task['id']} updated: \"{task['title']}\"")
        return 0
    except (KeyError, ValueError) as exc:
        ui.print_error(str(exc))
        return 1


def cmd_clear(args: argparse.Namespace) -> int:
    """Handle: python main.py clear"""
    count = manager.clear_done()
    if count == 0:
        ui.print_info("No completed tasks to clear.")
    else:
        ui.print_success(f"Cleared {count} completed task{'s' if count != 1 else ''}.")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Handle: python main.py stats"""
    stats = manager.get_stats()
    ui.print_stats(stats)
    return 0


# ── Argument parser ───────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog        = "task",
        description = "⚡ Task Manager CLI – manage tasks right from your terminal.",
        formatter_class = argparse.RawTextHelpFormatter,
        epilog      = (
            "Examples:\n"
            "  task add \"Write unit tests\" --priority high --tags work\n"
            "  task list --filter pending\n"
            "  task done 3\n"
            "  task delete 7\n"
            "  task edit 2 --title \"New title\" --priority low\n"
            "  task clear\n"
            "  task stats\n"
        ),
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    # ── add ──────────────────────────────────────────────────────────────
    p_add = subparsers.add_parser("add", help="Add a new task")
    p_add.add_argument("title", help="Task description")
    p_add.add_argument(
        "--priority", "-p",
        choices = ["low", "normal", "high"],
        default = "normal",
        help    = "Task priority (default: normal)",
    )
    p_add.add_argument(
        "--tags", "-t",
        nargs   = "+",
        metavar = "TAG",
        help    = "One or more tags (e.g. --tags work home)",
    )
    p_add.set_defaults(func=cmd_add)

    # ── list ─────────────────────────────────────────────────────────────
    p_list = subparsers.add_parser("list", help="List tasks")
    p_list.add_argument(
        "--filter", "-f",
        choices = ["all", "pending", "done"],
        default = "all",
        help    = "Filter by status (default: all)",
    )
    p_list.add_argument(
        "--priority", "-p",
        choices = ["low", "normal", "high"],
        default = None,
        help    = "Filter by priority",
    )
    p_list.add_argument(
        "--tag", "-t",
        default = None,
        help    = "Filter by tag",
    )
    p_list.set_defaults(func=cmd_list)

    # ── done ─────────────────────────────────────────────────────────────
    p_done = subparsers.add_parser("done", help="Mark a task as completed")
    p_done.add_argument("id", type=int, help="Task ID")
    p_done.set_defaults(func=cmd_done)

    # ── delete ───────────────────────────────────────────────────────────
    p_del = subparsers.add_parser("delete", aliases=["rm"], help="Delete a task")
    p_del.add_argument("id", type=int, help="Task ID")
    p_del.set_defaults(func=cmd_delete)

    # ── edit ─────────────────────────────────────────────────────────────
    p_edit = subparsers.add_parser("edit", help="Edit an existing task")
    p_edit.add_argument("id", type=int, help="Task ID")
    p_edit.add_argument("--title",    "-T", default=None, help="New title")
    p_edit.add_argument("--priority", "-p", choices=["low","normal","high"], default=None)
    p_edit.add_argument("--tags",     "-t", nargs="+", metavar="TAG", default=None)
    p_edit.set_defaults(func=cmd_edit)

    # ── clear ─────────────────────────────────────────────────────────────
    p_clear = subparsers.add_parser("clear", help="Remove all completed tasks")
    p_clear.set_defaults(func=cmd_clear)

    # ── stats ─────────────────────────────────────────────────────────────
    p_stats = subparsers.add_parser("stats", help="Show task statistics")
    p_stats.set_defaults(func=cmd_stats)

    return parser


# ── Entry point ───────────────────────────────────────────────────────────

def main(argv: list | None = None) -> int:
    ui.print_banner()
    parser = build_parser()
    args   = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
