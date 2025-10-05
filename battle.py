# battle.py
from __future__ import annotations

import os
import random
import json
from typing import List, Tuple, Optional

from utils import Ansi, hp_bar, ascii_header
from characters import Character, Protagonist
from effects import Downed, Guard
from enemies import Mob, Boss

# Результат действия: (value, is_crit, one_more)
ActionResult = Tuple[int, bool, bool]


class Battle:
    def __init__(self, party: List[Character], enemies: List[Character], name: str = "Схватка"):
        self.party = party
        self.enemies = enemies
        self.name = name
        self.turn = 0

    # ---------- helpers ----------
    def living_party(self) -> List[Character]:
        return [p for p in self.party if p.is_alive]

    def living_enemies(self) -> List[Character]:
        return [e for e in self.enemies if e.is_alive]

    def is_over(self) -> bool:
        return not self.living_party() or not self.living_enemies()

    def ascii_status(self) -> None:
        print("\n" + Ansi.GREY + "—" * 78 + Ansi.RESET)
        print(Ansi.BOLD + "Пати:" + Ansi.RESET)
        for p in self.party:
            effs = ", ".join(f"{e.name}({e.duration})" for e in p.effects) or "-"
            print(
                f"  {p.name:12} "
                f"HP {hp_bar(p.hp, p.max_hp)} {p.hp:>3}/{p.max_hp:<3}  "
                f"MP {p.mp:>3}/{p.max_mp:<3}  "
                f"{'DOWN ' if p.down else ''}"
                f"  [Эффекты: {effs}]"
            )
        print(Ansi.BOLD + "Враги:" + Ansi.RESET)
        for e in self.enemies:
            effs = ", ".join(f"{ef.name}({ef.duration})" for ef in e.effects) or "-"
            weak = ", ".join(w.name.lower() for w in getattr(e, "weaknesses", [])) or "-"
            res = ", ".join(r.name.lower() for r in getattr(e, "resists", [])) or "-"
            print(
                f"  {e.name:12} "
                f"HP {hp_bar(e.hp, e.max_hp)} {e.hp:>3}/{e.max_hp:<3}  "
                f"{'DOWN ' if e.down else ''}"
                f"  [Эффекты: {effs}]  [weak: {weak}] [res: {res}]"
            )
        print(Ansi.GREY + "—" * 78 + Ansi.RESET)

    def all_out_attack(self) -> None:
        # если все живые враги повалены — командная атака
        if self.living_enemies() and all(getattr(e, "down", False) for e in self.living_enemies()):
            ascii_header("ALL-OUT ATTACK!")
            for e in self.living_enemies():
                dmg = e.receive_damage(25, None)
                e.down = False
                print(f"Командная атака бьёт {e.name} на {dmg}!")

    # ---------- enemy AI only ----------
    def enemy_ai(self, unit: Character) -> None:
        """
        Действие ИИ для врага. Если вернулся one_more=True — враг сразу ходит ещё раз.
        """
        if not unit.is_alive or not self.living_party():
            return

        if isinstance(unit, Boss):
            unit.pick_strategy()
            name, _ = unit.strategy.decide(unit, [unit], self.living_party())
            if name in unit.skills:
                tup = unit.use_skill(name, [unit], self.living_party())
            else:
                tup = unit.basic_attack(random.choice(self.living_party()))
        elif isinstance(unit, Mob):
            if unit.mp >= 6 and random.random() < 0.5:
                tup = unit.use_skill("Пламя", [unit], self.living_party())
            else:
                tup = unit.basic_attack(random.choice(self.living_party()))
        else:
            tup = unit.basic_attack(random.choice(self.living_party()))

        _, _, one_more = self._normalize_action_result(tup)
        if one_more and not self.is_over():
            print(Ansi.YELLOW + f"1 MORE! {unit.name} (враг) получает дополнительный ход!" + Ansi.RESET)
            self.enemy_ai(unit)

    # ---------- меню с поддержкой «Назад» ----------
    def choose_from_list(self, title: str, options: List[str], allow_back: bool = False) -> int:
        print(Ansi.CYAN + title + Ansi.RESET)
        for i, text in enumerate(options, 1):
            print(f"  {i}) {text}")
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

    def choose_enemy_target(self, allow_back: bool = False) -> Optional[Character]:
        enemies = self.living_enemies()
        opts = [
            f"{e.name} | HP {e.hp}/{e.max_hp} | weak: {', '.join(w.name.lower() for w in e.weaknesses) or '-'} | "
            f"res: {', '.join(r.name.lower() for r in e.resists) or '-'}"
            for e in enemies
        ]
        idx = self.choose_from_list("Выбери цель (враг):", opts, allow_back=allow_back)
        if idx == -1:
            return None
        return enemies[idx]

    def choose_ally_target(self, allow_back: bool = False) -> Optional[Character]:
        allies = self.living_party()
        opts = [f"{a.name} | HP {a.hp}/{a.max_hp}" for a in allies]
        idx = self.choose_from_list("Выбери цель (союзник):", opts, allow_back=allow_back)
        if idx == -1:
            return None
        return allies[idx]

    def use_item_flow(self, unit: Character) -> Tuple[bool, bool]:
        """
        Возвращает (used, one_more). Предметы не дают 1 MORE => False.
        Поддерживает «Назад».
        """
        if not unit.inventory:
            print("Инвентарь пуст.")
            return False, False
        opts = [f"{it.name} — {it.description}" for it in unit.inventory]
        i_idx = self.choose_from_list("Выбери предмет:", opts, allow_back=True)
        if i_idx == -1:
            return False, False
        item = unit.inventory[i_idx]
        target = self.choose_ally_target(allow_back=True)
        if target is None:
            return False, False
        print(item.use(unit, target))
        del unit.inventory[i_idx]  # одноразовый
        return True, False

    def persona_switch_flow(self, unit: Protagonist) -> None:
        personas = list(unit.personas.keys())
        idx = self.choose_from_list("Смена персоны:", personas, allow_back=True)
        if idx == -1:
            return
        picked = personas[idx]
        if unit.switch_persona(picked):
            print(f"{Ansi.YELLOW}{unit.name} меняет персону на {picked}!{Ansi.RESET}")
        else:
            print("Не удалось сменить персону (возможно, уже меняли в этот ход).")

    def skills_menu_flow(self, unit: Character) -> Tuple[bool, bool]:
        """
        Возвращает (casted: bool, one_more: bool). Поддерживает «Назад».
        """
        if not unit.skills:
            print("Нет доступных навыков.")
            return False, False

        names = list(unit.skills.keys())
        display = []
        for n in names:
            sk = unit.skills[n]
            cd = unit._cooldowns.get(n, 0)
            tag_cd = f", CD {cd}" if cd > 0 else ""
            effective = any(sk.element in e.weaknesses for e in self.living_enemies())
            tag_eff = " (эффективно)" if effective else ""
            desc = f" — {sk.description}" if getattr(sk, "description", "") else ""
            display.append(f"{sk.name} ({sk.element.name.lower()}) MP {sk.mp_cost}{tag_cd}{tag_eff}{desc}")

        s_idx = self.choose_from_list("Выбери навык:", display, allow_back=True)
        if s_idx == -1:
            return False, False

        sk_name = names[s_idx]
        sk = unit.skills[sk_name]

        if unit.is_cd(sk.name):
            print("Этот навык на перезарядке.")
            return False, False
        if unit.mp < sk.mp_cost:
            print("Недостаточно MP.")
            return False, False

        res = unit.use_skill(sk_name, self.living_party(), self.living_enemies())
        _, _, one_more = self._normalize_action_result(res)
        return True, one_more

    # ---------- управление игроком ----------
    def player_turn(self, unit: Character) -> None:
        """
        Интерактивное меню для героя. Если действие даёт one_more=True — немедленный повторный ход.
        """
        while True:
            print(f"\nХод {unit.name}. Что будем делать?")
            base_actions = ["Атака", "Навык", "Предмет", "Защита"]
            if isinstance(unit, Protagonist):
                base_actions.insert(1, "Смена персоны")
            choice = self.choose_from_list("Действия:", base_actions)
            action = base_actions[choice]

            if action == "Атака":
                if self.living_enemies():
                    target = self.choose_enemy_target(allow_back=True)
                    if target is None:
                        continue  # назад в главное меню
                    res = unit.basic_attack(target)
                    _, _, one_more = self._normalize_action_result(res)
                    if one_more:
                        print(Ansi.YELLOW + f"1 MORE! {unit.name} получает дополнительный ход!" + Ansi.RESET)
                        continue
                return

            if action == "Смена персоны":
                self.persona_switch_flow(unit)  # не тратит действие
                continue  # вернуться в меню для действия

            if action == "Навык":
                casted, one_more = self.skills_menu_flow(unit)
                if casted:
                    if one_more:
                        print(Ansi.YELLOW + f"1 MORE! {unit.name} получает дополнительный ход!" + Ansi.RESET)
                        continue
                    return
                # «Назад» или неудачный каст — вернуться к главному меню
                continue

            if action == "Предмет":
                used, _ = self.use_item_flow(unit)
                if used:
                    return
                continue  # «Назад» — назад в меню

            if action == "Защита":
                unit.add_effect(Guard(0.5, 1))  # 50% снижения урона до начала следующего хода
                print(Ansi.GREEN + f"{unit.name} принимает защитную стойку!" + Ansi.RESET)
                return

    # ---------- ход ----------
    def turn_for(self, unit: Character) -> None:
        if not unit.is_alive:
            return

        unit.tick_effects_start()
        if not unit.is_alive:
            return

        if any(isinstance(e, Downed) for e in unit.effects):
            print(Ansi.GREY + f"{unit.name} оглушён и пропускает ход." + Ansi.RESET)
            unit.tick_effects_end()
            unit.down = False
            return

        before_down = [e.down for e in self.living_enemies()]

        if unit in self.party:
            self.player_turn(unit)
        else:
            self.enemy_ai(unit)

        after_down = [e.down for e in self.living_enemies()]
        # Доп. гарантия 1 MORE при новом Down (остается как дополнительная связка)
        if any(b2 and not b1 for b1, b2 in zip(before_down, after_down)):
            print(Ansi.YELLOW + f"1 MORE! {unit.name} получает дополнительный ход!" + Ansi.RESET)
            enemies = self.living_enemies()
            if enemies:
                t = min(enemies, key=lambda x: x.hp)
                unit.basic_attack(t)

        self.all_out_attack()
        unit.reduce_cooldowns()
        unit.tick_effects_end()

    # ---------- снапшот боя ----------
    def _char_state(self, c: Character):
        return {
            "name": c.name,
            "hp": c.hp,
            "max_hp": c.max_hp,
            "mp": c.mp,
            "max_mp": c.max_mp,
            "down": getattr(c, "down", False),
            "weak": [w.name for w in getattr(c, "weaknesses", [])],
            "res": [r.name for r in getattr(c, "resists", [])],
            "effects": [{"name": e.name, "duration": e.duration, "desc": getattr(e, "description", "")} for e in c.effects],
        }

    def _battle_snapshot(self):
        return {
            "turn": self.turn,
            "party": [self._char_state(p) for p in self.party],
            "enemies": [self._char_state(e) for e in self.enemies],
        }

    def _save_snapshot(self):
        os.makedirs("saves", exist_ok=True)
        with open(os.path.join("saves", "battle_state.json"), "w", encoding="utf-8") as f:
            json.dump(self._battle_snapshot(), f, ensure_ascii=False, indent=2)

    # ---------- публичный запуск ----------
    def run(self) -> bool:
        ascii_header(self.name)
        self.ascii_status()

        while not self.is_over():
            self.turn += 1
            print(Ansi.BLUE + f"\n— Раунд {self.turn} —" + Ansi.RESET)

            # порядок по ловкости, оглушённые позже
            units = [u for u in self.living_party() + self.living_enemies() if u.is_alive]
            units.sort(key=lambda u: (u.down, -u.agility))

            for u in units:
                if self.is_over():
                    break
                side = "Пати" if u in self.party else "Враг"
                print(Ansi.DIM + f"[{side}] Ходит {u.name}" + Ansi.RESET)
                self.turn_for(u)
                self.ascii_status()

            # сейв после каждого полного раунда
            self._save_snapshot()

        win = bool(self.living_party())
        print(Ansi.BOLD + ("Победа!" if win else "Поражение...") + Ansi.RESET)
        return win

    # ---------- утилита ----------
    def _normalize_action_result(self, res) -> ActionResult:
        if res is None:
            return 0, False, False
        if isinstance(res, tuple) and len(res) == 3:
            return res[0], bool(res[1]), bool(res[2])
        if isinstance(res, tuple) and len(res) == 2:
            return res[0], bool(res[1]), False
        if isinstance(res, int):
            return res, False, False
        return 0, False, False
4