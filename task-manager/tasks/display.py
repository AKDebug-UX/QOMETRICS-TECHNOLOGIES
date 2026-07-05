from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

PRI_COLOR = {
    "low":    Fore.CYAN,
    "normal": Fore.WHITE,
    "high":   Fore.RED + Style.BRIGHT,
}

PRI_ICON = {"low": "▽", "normal": "◇", "high": "▲"}
STATUS_ICON = {"pending": "○", "done": "✓"}


def _pri(priority):
    return f"{PRI_COLOR.get(priority, Fore.WHITE)}{PRI_ICON.get(priority, '?')} {priority.upper()}"


def _tag_str(tags):
    if not tags:
        return ""
    return "  " + " ".join(f"{Fore.MAGENTA}#{t}" for t in tags)


def print_task_row(task):
    done = task["status"] == "done"
    id_s = f"{Fore.YELLOW}{task['id']:>3}"
    icon = f"{Fore.GREEN if done else Fore.BLUE}{STATUS_ICON[task['status']]}"
    title = f"{Style.DIM}{task['title']}" if done else task["title"]
    tags = _tag_str(task.get("tags", []))
    date = f"{Style.DIM}{task['created_at'][:10]}"
    print(f"  {id_s}  {icon}  {title}{tags}  [{_pri(task['priority'])}]  {date}")


def print_task_list(tasks, title="Tasks"):
    sep()
    print(f"  {Style.BRIGHT}{title}  ({len(tasks)} item{'s' if len(tasks) != 1 else ''})")
    sep()
    if not tasks:
        print(f"  {Style.DIM}Nothing here yet.")
    else:
        print(f"  {Style.DIM}{'ID':>3}  {'':1}  {'Title':<38}  {'Priority':<14}  Date")
        print(f"  {Style.DIM}{'─' * 72}")
        for t in tasks:
            print_task_row(t)
    sep()


def print_success(msg):
    print(f"\n  {Fore.GREEN}✓  {msg}\n")


def print_error(msg):
    print(f"\n  {Fore.RED}✗  {msg}\n")


def print_info(msg):
    print(f"\n  {Fore.CYAN}→  {msg}\n")


def print_warning(msg):
    print(f"\n  {Fore.YELLOW}!  {msg}\n")


def print_stats(stats):
    sep()
    print(f"  {Style.BRIGHT}Stats")
    sep()

    total = stats["total"]
    done = stats["done"]
    filled = round((done / total) * 20) if total > 0 else 0
    bar = f"{Fore.GREEN}{'█' * filled}{Style.DIM}{'░' * (20 - filled)}"
    pct = f"{done / total * 100:.0f}%" if total > 0 else "0%"

    print(f"  {bar}  {Fore.GREEN}{done}{Style.RESET_ALL}/{total} done  ({pct})")
    print()
    print(f"  {Fore.BLUE}○{Style.RESET_ALL}  pending   {stats['pending']}")
    print(f"  {Fore.GREEN}✓{Style.RESET_ALL}  done      {done}")
    print()
    for p, c in stats["by_priority"].items():
        print(f"  {PRI_COLOR.get(p, '')}{PRI_ICON.get(p, '')}  {p:<10}{c}")
    sep()


def print_banner():
    print()
    print(f"  {Fore.CYAN + Style.BRIGHT}[ task manager ]  v1.0")
    print()


def sep():
    print(f"  {Style.DIM}{'─' * 72}")
