"""
tasks/display.py
────────────────
Colorama-powered output helpers.
All output goes through this module so the rest of the codebase
stays free of print/colour logic.
"""

from colorama import Fore, Style, init as colorama_init

# Auto-reset colour after every print
colorama_init(autoreset=True)

# ── Colour palette ─────────────────────────────────────────────────────────
PRIORITY_COLOURS = {
    "low":    Fore.CYAN,
    "normal": Fore.WHITE,
    "high":   Fore.RED + Style.BRIGHT,
}

PRIORITY_ICONS = {
    "low":    "▽",
    "normal": "◇",
    "high":   "▲",
}

STATUS_ICONS = {
    "pending": "○",
    "done":    "✓",
}


# ── Internal helpers ───────────────────────────────────────────────────────

def _priority_str(priority: str) -> str:
    colour = PRIORITY_COLOURS.get(priority, Fore.WHITE)
    icon   = PRIORITY_ICONS.get(priority, "?")
    return f"{colour}{icon} {priority.upper()}{Style.RESET_ALL}"


def _tags_str(tags: list) -> str:
    if not tags:
        return ""
    tag_parts = " ".join(f"{Fore.MAGENTA}#{t}{Style.RESET_ALL}" for t in tags)
    return f"  {tag_parts}"


# ── Public output functions ────────────────────────────────────────────────

def print_task_row(task: dict, index: int | None = None) -> None:
    """Print a single task row in the task list."""
    status   = task["status"]
    is_done  = status == "done"
    dim      = Style.DIM if is_done else ""

    # ID
    id_str     = f"{Fore.YELLOW}{task['id']:>3}{Style.RESET_ALL}"
    # Status icon
    status_col = Fore.GREEN if is_done else Fore.BLUE
    icon       = f"{status_col}{STATUS_ICONS[status]}{Style.RESET_ALL}"
    # Title (dim if done, strikethrough-ish with dim)
    title      = f"{dim}{task['title']}{Style.RESET_ALL}"
    if is_done:
        title  = f"{Style.DIM}{task['title']}{Style.RESET_ALL}"
    # Priority
    pri_str    = _priority_str(task["priority"])
    # Tags
    tags_str   = _tags_str(task.get("tags", []))
    # Date
    date       = task["created_at"][:10]
    date_str   = f"{Style.DIM}{date}{Style.RESET_ALL}"

    print(f"  {id_str}  {icon}  {title}{tags_str}  [{pri_str}]  {date_str}")


def print_task_list(tasks: list, title: str = "Tasks") -> None:
    """Print a formatted, colour-coded task list."""
    _print_separator()
    print(f"  {Fore.WHITE + Style.BRIGHT}{title}{Style.RESET_ALL}  ({len(tasks)} item{'s' if len(tasks) != 1 else ''})")
    _print_separator()

    if not tasks:
        print(f"  {Style.DIM}No tasks found.{Style.RESET_ALL}")
    else:
        # Header
        print(
            f"  {Fore.WHITE + Style.DIM}"
            f"{'ID':>3}  {'':1}  {'Title':<35}  {'Priority':<16}  Date"
            f"{Style.RESET_ALL}"
        )
        print(f"  {Style.DIM}{'─' * 72}{Style.RESET_ALL}")
        for task in tasks:
            print_task_row(task)

    _print_separator()


def print_success(message: str) -> None:
    print(f"\n  {Fore.GREEN}✓  {message}{Style.RESET_ALL}\n")


def print_error(message: str) -> None:
    print(f"\n  {Fore.RED}✗  {message}{Style.RESET_ALL}\n")


def print_info(message: str) -> None:
    print(f"\n  {Fore.CYAN}ℹ  {message}{Style.RESET_ALL}\n")


def print_warning(message: str) -> None:
    print(f"\n  {Fore.YELLOW}⚠  {message}{Style.RESET_ALL}\n")


def print_stats(stats: dict) -> None:
    """Print a colourful summary panel."""
    _print_separator()
    print(f"  {Fore.WHITE + Style.BRIGHT}Task Statistics{Style.RESET_ALL}")
    _print_separator()

    total   = stats["total"]
    done    = stats["done"]
    pending = stats["pending"]

    # Progress bar
    filled  = round((done / total) * 20) if total > 0 else 0
    bar     = f"{Fore.GREEN}{'█' * filled}{Style.DIM}{'░' * (20 - filled)}{Style.RESET_ALL}"
    pct     = f"{(done / total * 100):.0f}%" if total > 0 else "0%"

    print(f"  {bar}  {Fore.GREEN}{done}{Style.RESET_ALL}/{Fore.WHITE}{total}{Style.RESET_ALL} done  ({pct})")
    print()
    print(f"  {Fore.BLUE}○{Style.RESET_ALL}  Pending  : {Fore.WHITE + Style.BRIGHT}{pending}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}✓{Style.RESET_ALL}  Completed: {Fore.WHITE + Style.BRIGHT}{done}{Style.RESET_ALL}")
    print()

    for priority, count in stats["by_priority"].items():
        pri_col = PRIORITY_COLOURS.get(priority, Fore.WHITE)
        icon    = PRIORITY_ICONS.get(priority, "?")
        print(f"  {pri_col}{icon}  {priority.capitalize():<8}{Style.RESET_ALL}: {count}")

    _print_separator()


def print_banner() -> None:
    """Print the app header banner."""
    print()
    print(f"  {Fore.CYAN + Style.BRIGHT}╔══════════════════════════════╗{Style.RESET_ALL}")
    print(f"  {Fore.CYAN + Style.BRIGHT}║  ⚡  Task Manager CLI  v1.0  ║{Style.RESET_ALL}")
    print(f"  {Fore.CYAN + Style.BRIGHT}╚══════════════════════════════╝{Style.RESET_ALL}")
    print()


def _print_separator() -> None:
    print(f"  {Style.DIM}{'─' * 74}{Style.RESET_ALL}")
