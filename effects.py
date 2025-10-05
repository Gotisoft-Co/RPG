# effects.py (с описаниями)
from __future__ import annotations
from abc import ABC
from utils import Ansi

class Effect(ABC):
    def __init__(self, name: str, duration: int, description: str = ""):
        self.name = name
        self.duration = duration
        self.description = description
    def on_apply(self, target: "Character"): ...
    def on_expire(self, target: "Character"): ...
    def on_turn_start(self, target: "Character"): ...
    def on_turn_end(self, target: "Character"): self.duration -= 1
    @property
    def expired(self)->bool: return self.duration<=0

class Poison(Effect):
    def __init__(self, dmg_per_turn: int, duration: int=3):
        super().__init__("Яд", duration, description="Наносит урон каждый ход.")
        self.dmg=dmg_per_turn
    def on_turn_start(self, target: "Character"):
        if getattr(target,'is_alive',False):
            target.receive_damage(self.dmg, target.last_element if hasattr(target,'last_element') else None)
            print(f"{Ansi.MAGENTA}{target.name} страдает от яда ({self.dmg}).{Ansi.RESET}")

class Regen(Effect):
    def __init__(self, heal: int, duration: int=3):
        super().__init__("Реген", duration, description="Восстанавливает HP каждый ход.")
        self.heal_each=heal
    def on_turn_end(self, target: "Character"):
        super().on_turn_end(target); target.hp += self.heal_each
        print(f"{Ansi.GREEN}{target.name} регенерирует {self.heal_each} HP.{Ansi.RESET}")

class Shield(Effect):
    def __init__(self, ratio: float=0.5, duration: int=2):
        super().__init__("Щит", duration, description="Снижает получаемый урон на заданный процент.")
        self.ratio=ratio
    def on_apply(self, target: "Character"): target._shield_ratio = max(getattr(target,"_shield_ratio",0.0), self.ratio)
    def on_expire(self, target: "Character"): target._shield_ratio = 0.0

class Guard(Effect):
    def __init__(self, ratio: float = 0.5, duration: int = 1):
        # 50% снижения урона до начала следующего хода
        super().__init__("Защита", duration, description="Снижает получаемый урон до начала следующего хода.")
        self.ratio = ratio

    def on_apply(self, target: "Character"):
        # стакаем с уже активным щитом, берём максимум
        target._shield_ratio = max(getattr(target, "_shield_ratio", 0.0), self.ratio)

    # ВАЖНО: защита должна пережить конец текущего хода,
    # поэтому на конце хода НИЧЕГО не уменьшаем.
    def on_turn_end(self, target: "Character"):
        pass

    # А вот в начале следующего хода — снимаем действие защиты
    # (делаем _shield_ratio=0 сразу, даже если удаление эффекта произойдёт позже).
    def on_turn_start(self, target: "Character"):
        self.duration -= 1
        if self.duration <= 0:
            target._shield_ratio = 0.0

    def on_expire(self, target: "Character"):
        target._shield_ratio = 0.0

class Silence(Effect):
    def __init__(self, duration: int=1):
        super().__init__("Немота", duration, description="Запрещает использовать навыки.")

class Downed(Effect):
    def __init__(self, duration: int=1):
        super().__init__("Оглушение", duration, description="Пропускает ход из-за оглушения.")
