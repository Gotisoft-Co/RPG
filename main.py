# main.py
from __future__ import annotations

import random
from typing import List, Literal, Optional

from utils import Ansi, ascii_header
from characters import Warrior, Mage, Healer, Thief, Protagonist
from items import Potion, Ether
from personas import STARTER_PERSONAS
from corridor import corridor_run
from battle import Battle
from enemies import Boss

Difficulty = Literal["easy", "normal", "hard"]


# -------- генерация/настройка пати --------
def generate_party() -> List:
    mc = Protagonist("Протагонист", STARTER_PERSONAS)
    party = [mc, Mage("Маг"), Healer("Хилер"), Thief("Вор")]
    party[2].inventory.extend([Potion(), Ether()])  # чуть стартовых предметов
    return party


def difficulty_tune(party, difficulty: Difficulty):
    mult = {"easy": 1.15, "normal": 1.0, "hard": 0.8}[difficulty]
    for p in party:
        p.max_hp = int(p.max_hp * mult)
        p.hp = p.max_hp
        p.max_mp = int(p.max_mp * mult)
        p.mp = p.max_mp


def choose_from_list(title: str, options: List[str], allow_back: bool = False) -> int:
    print(Ansi.CYAN + title + Ansi.RESET)
    for i, t in enumerate(options, 1):
        print(f"  {i}) {t}")
    if allow_back:
        print("  0) Назад")
    while True:
        s = input("> ").strip()
        if allow_back and s == "0":
            return -1
        if s.isdigit():
            idx = int(s) - 1
            if 0 <= idx < len(options):
                return idx
        print("Введите номер из списка.")


def prompt_int(title: str, default: Optional[int] = None) -> Optional[int]:
    print(Ansi.CYAN + title + Ansi.RESET)
    if default is not None:
        print(f"(пусто — оставить {default})")
    s = input("> ").strip()
    if s == "" and default is not None:
        return default
    if s.lower() in ("none", "нет", "пусто"):
        return None
    try:
        return int(s)
    except ValueError:
        print("Введите целое число или оставьте пустым.")
        return prompt_int(title, default)


def build_party_menu() -> list:
    # ГГ всегда в пати
    picked = [Protagonist("Протагонист", STARTER_PERSONAS)]

    # Остальные слоты выбираем из этого пула (без ГГ)
    pool = [
        ("Воин", Warrior),
        ("Маг", Mage),
        ("Хилер", Healer),
        ("Вор", Thief),
    ]

    while len(picked) < 4 and pool:
        print(Ansi.CYAN + f"Слот {len(picked)}/4 — выбери героя:" + Ansi.RESET)
        for i, (n, _) in enumerate(pool, 1):
            print(f"  {i}) {n}")
        if len(picked) >= 2:  # чтобы можно было закончить набор, когда уже 2+ бойцов
            print("  0) Завершить набор")

        s = input("> ").strip()
        if s == "0" and len(picked) >= 2:
            break
        if s.isdigit() and 1 <= int(s) <= len(pool):
            name, cls = pool.pop(int(s) - 1)   # убираем из пула, чтобы не было дубликатов
            picked.append(cls(name))
        else:
            print("Неверный выбор.")

    # если меньше 4 — просто оставляем как есть (ГГ + выбранные)
    return picked

# -------- игровой запуск --------
def run_game_flow(difficulty: Difficulty, seed: Optional[int], party_override: Optional[List] = None) -> int:
    if seed is not None:
        random.seed(seed)
        print(Ansi.GREY + f"Seed: {seed}" + Ansi.RESET)

    party = party_override if party_override else generate_party()
    difficulty_tune(party, difficulty)

    # Коридор из стычек
    if not corridor_run(party, battles=3):
        print("Герои не дошли до босса…")
        return 1

    # Босс
    print()
    ascii_header("Босс: Страж Коридора")
    b = Battle(party, [Boss("Страж Коридора")], name="Бой с боссом")
    return 0 if b.run() else 2


def print_title(difficulty: Difficulty, seed: Optional[int], party_override: Optional[List]):
    ascii_header("Persona-like ASCII RPG")
    diff_txt = {"easy": "Лёгкая", "normal": "Нормальная", "hard": "Сложная"}[difficulty]
    print(f"{Ansi.BOLD}Текущие настройки:{Ansi.RESET}")
    print(f"  Сложность: {diff_txt}")
    print(f"  Seed (случайность): {'<случайный>' if seed is None else seed}")
    if party_override:
        names = ", ".join([p.name for p in party_override])
        print(f"  Пати: {names}")
    print()


def main():
    difficulty: Difficulty = "normal"
    seed: Optional[int] = None
    party_override: Optional[List] = None

    while True:
        print_title(difficulty, seed, party_override)
        choice = choose_from_list(
            "Главное меню",
            [
                "Новая игра",
                "Выбрать сложность",
                "Установить seed случайности",
                "Собрать пати",
                "Справка (управление)",
                "Выход",
            ],
        )

        if choice == 0:  # Новая игра
            _ = run_game_flow(difficulty, seed, party_override)
            print()
            input(Ansi.GREY + "Нажмите Enter, чтобы вернуться в меню…" + Ansi.RESET)

        elif choice == 1:  # Сложность
            i = choose_from_list("Выбери сложность:", ["Лёгкая", "Нормальная", "Сложная"], allow_back=True)
            if i != -1:
                difficulty = ["easy", "normal", "hard"][i]  # type: ignore[index]
                print(Ansi.GREEN + "Сложность обновлена." + Ansi.RESET)

        elif choice == 2:  # Seed
            seed = prompt_int("Укажи seed (целое) или 'none' для случайного", seed)
            print(Ansi.GREEN + "Seed обновлён." + Ansi.RESET)

        elif choice == 3:  # Собрать пати
            party_override = build_party_menu()
            print(Ansi.GREEN + "Состав пати обновлён." + Ansi.RESET)

        elif choice == 4:  # Справка
            print()
            ascii_header("Справка")
            print(
                "— Пошаговая ASCII-RPG с механиками Persona:\n"
                "  слабости/резисты, 1 MORE!, All-Out Attack, смена персоны у Протагониста.\n\n"
                "— Управление боем:\n"
                "  • Атака — выбрать цель.\n"
                "  • Навык — список умений с элементом и описанием (0 — Назад).\n"
                "  • Предмет — применить к союзнику (0 — Назад).\n"
                "  • Защита — пропуск хода со снижением урона.\n"
                "  • Смена персоны — только у Протагониста, не тратит действие.\n\n"
                "— Подсказки:\n"
                "  • У врагов видны weak/res для подбора стихии.\n"
                "  • Попадание в слабость даёт 1 MORE! — сразу ещё ход.\n"
            )
            input(Ansi.GREY + "Enter — назад" + Ansi.RESET)

        elif choice == 5:  # Выход
            print(Ansi.YELLOW + "До встречи!" + Ansi.RESET)
            return


if __name__ == "__main__":
    main()
