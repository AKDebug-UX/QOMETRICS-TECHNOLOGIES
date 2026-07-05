#!/usr/bin/env python3
import argparse
import sys

from tasks import display as ui
from tasks import manager


def cmd_add(args):
    try:
        task = manager.add_task(args.title, priority=args.priority, tags=args.tags or [])
        ui.print_success(f"Task #{task['id']} added — \"{task['title']}\" [{task['priority']}]")
        return 0
    except ValueError as e:
        ui.print_error(str(e))
        return 1


def cmd_list(args):
    try:
        tasks = manager.list_tasks(
            status_filter=args.filter,
            priority_filter=args.priority,
            tag_filter=args.tag,
        )
        labels = {"all": "All Tasks", "pending": "Pending", "done": "Done"}
        ui.print_task_list(tasks, title=labels.get(args.filter, "Tasks"))
        return 0
    except ValueError as e:
        ui.print_error(str(e))
        return 1


def cmd_done(args):
    try:
        task = manager.mark_done(args.id)
        ui.print_success(f"Task #{task['id']} done — \"{task['title']}\"")
        return 0
    except KeyError as e:
        ui.print_error(str(e))
        return 1
    except ValueError as e:
        ui.print_warning(str(e))
        return 0


def cmd_delete(args):
    try:
        task = manager.delete_task(args.id)
        ui.print_success(f"Deleted task #{task['id']} — \"{task['title']}\"")
        return 0
    except KeyError as e:
        ui.print_error(str(e))
        return 1


def cmd_edit(args):
    if args.title is None and args.priority is None and args.tags is None:
        ui.print_error("Nothing to update. Use --title, --priority, or --tags.")
        return 1
    try:
        task = manager.edit_task(args.id, title=args.title, priority=args.priority, tags=args.tags)
        ui.print_success(f"Task #{task['id']} updated — \"{task['title']}\"")
        return 0
    except (KeyError, ValueError) as e:
        ui.print_error(str(e))
        return 1


def cmd_clear(args):
    n = manager.clear_done()
    if n == 0:
        ui.print_info("No completed tasks to remove.")
    else:
        ui.print_success(f"Cleared {n} completed task{'s' if n != 1 else ''}.")
    return 0


def cmd_stats(args):
    ui.print_stats(manager.get_stats())
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog="task",
        description="Task Manager CLI",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "examples:\n"
            "  task add \"Fix the login bug\" --priority high --tags work\n"
            "  task list --filter pending\n"
            "  task done 3\n"
            "  task delete 5\n"
            "  task edit 2 --priority low\n"
            "  task stats\n"
        ),
    )

    sub = p.add_subparsers(dest="command", metavar="command")
    sub.required = True

    # add
    add = sub.add_parser("add", help="add a new task")
    add.add_argument("title")
    add.add_argument("--priority", "-p", choices=["low","normal","high"], default="normal")
    add.add_argument("--tags", "-t", nargs="+", metavar="TAG")
    add.set_defaults(func=cmd_add)

    # list
    ls = sub.add_parser("list", help="list tasks")
    ls.add_argument("--filter", "-f", choices=["all","pending","done"], default="all")
    ls.add_argument("--priority", "-p", choices=["low","normal","high"], default=None)
    ls.add_argument("--tag", "-t", default=None)
    ls.set_defaults(func=cmd_list)

    # done
    done = sub.add_parser("done", help="mark task as completed")
    done.add_argument("id", type=int)
    done.set_defaults(func=cmd_done)

    # delete
    rm = sub.add_parser("delete", aliases=["rm"], help="delete a task")
    rm.add_argument("id", type=int)
    rm.set_defaults(func=cmd_delete)

    # edit
    edit = sub.add_parser("edit", help="edit a task")
    edit.add_argument("id", type=int)
    edit.add_argument("--title", "-T", default=None)
    edit.add_argument("--priority", "-p", choices=["low","normal","high"], default=None)
    edit.add_argument("--tags", "-t", nargs="+", metavar="TAG", default=None)
    edit.set_defaults(func=cmd_edit)

    # clear
    clr = sub.add_parser("clear", help="remove all completed tasks")
    clr.set_defaults(func=cmd_clear)

    # stats
    st = sub.add_parser("stats", help="show statistics")
    st.set_defaults(func=cmd_stats)

    return p


def main(argv=None):
    ui.print_banner()
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
