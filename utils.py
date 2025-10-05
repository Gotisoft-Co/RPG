from __future__ import annotations
class Ansi:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    RED = "\033[31m"; GREEN = "\033[32m"; YELLOW = "\033[33m"; BLUE = "\033[34m"; MAGENTA = "\033[35m"; CYAN = "\033[36m"; GREY = "\033[90m"


def hp_bar(current: int, maximum: int, width: int = 20) -> str:
    maximum = max(1, maximum)
    filled = int(width * max(0, current) / maximum)
    color = Ansi.GREEN if current/maximum>0.6 else (Ansi.YELLOW if current/maximum>0.3 else Ansi.RED)
    return f"{color}[" + "#"*filled + "-"*(width-filled) + f"]{Ansi.RESET}"


def ascii_header(title: str) -> None:
    line = "=" * (len(title)+8)
    print(f"\n{Ansi.CYAN}{line}\n== {title} ==\n{line}{Ansi.RESET}")


def draw_corridor(position: int, length: int, boss_at: int) -> None:
    tiles = []
    for i in range(length+1):
        if i==boss_at: tiles.append(f"{Ansi.RED}[B]{Ansi.RESET}")
        elif i==position: tiles.append(f"{Ansi.YELLOW}[P]{Ansi.RESET}")
        else: tiles.append("[ ]")
    print("Коридор:", "-".join(tiles))